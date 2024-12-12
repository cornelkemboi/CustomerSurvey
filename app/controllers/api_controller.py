from flask import Blueprint, request, jsonify
from sqlalchemy import func, Float
from app.models.models import SurveyResponse, SurveyCategoryValue, Survey
from config import db

api_bp = Blueprint("api", __name__)


@api_bp.route('/api/forms', methods=['GET'])
def fetch_forms():
    """
    Fetches the distinct form definitions (formdef_id) from the Survey table.
    """
    try:
        # Query the Survey table for distinct formdef_ids
        forms = db.session.query(Survey.formdef_id).distinct().all()

        # Format the result as a list of dictionaries
        result = [{"id": form.formdef_id, "name": form.formdef_id} for form in forms]

        return jsonify(result)
    except Exception as e:
        print(f"Error fetching forms: {e}")
        return jsonify({"error": "Failed to fetch forms"}), 500


# @api_bp.route("/api/category_counts", methods=["GET"])
# def fetch_category_counts():
#     """
#     Fetches the count of entries for a specific survey and its categories, optionally filtered by category or role.
#     """
#     form_id = request.args.get("formdef_id")
#     category = request.args.get("category")
#     role = request.args.get("role")
#
#     if not form_id:
#         return jsonify({"error": "formdef_id is required"}), 400
#
#     # Start the query to fetch category counts
#     query = (
#         db.session.query(
#             SurveyCategoryValue.category,
#             SurveyCategoryValue.key,
#             func.sum(SurveyCategoryValue.value).label('total_value'),
#             func.count(SurveyCategoryValue.id).label('count')
#         )
#         .join(SurveyResponse, SurveyCategoryValue.survey_id == SurveyResponse.survey_id)
#         .join(Survey, Survey.id == SurveyResponse.survey_id)
#         .filter(Survey.formdef_id == form_id)
#         .group_by(SurveyCategoryValue.category, SurveyCategoryValue.key)
#         .order_by(SurveyCategoryValue.category, SurveyCategoryValue.key)  # Optional: order by category and key
#     )
#
#     # Apply optional filters
#     if category:
#         query = query.filter(SurveyCategoryValue.category == category)
#     if role:
#         query = query.filter(SurveyResponse.role == role)
#
#     # Execute the query
#     results = query.all()
#
#     # Function to replace long key names with Q1, Q2, etc.
#     def replace_key_suffix(key):
#         # Assuming keys are structured like "prod_1", "prod_2", etc.
#         suffix = key.split('_')[-1]  # Extract the suffix (the last part after underscore)
#         try:
#             suffix_num = int(suffix)  # Convert to integer
#             if suffix_num == 1:
#                 return f"Q{suffix_num}"
#             else:
#                 return f"Q{suffix_num}"  # For any other number (e.g., 2-9)
#         except ValueError:
#             return key  # Return original key if conversion fails
#
#     # Format the result as a dictionary grouped by category and key
#     output = {}
#     for category, key, total_value, count in results:
#         if category not in output:
#             output[category] = {}
#
#         new_key = replace_key_suffix(key)  # Replace long key name with Q format
#         output[category][new_key] = {
#             'total_value': total_value,
#             'count': count
#         }
#
#     return jsonify(output)

@api_bp.route("/api/category_counts", methods=["GET"])
def fetch_category_counts():
    form_id = request.args.get("formdef_id")
    category = request.args.get("category")
    role = request.args.get("role")

    if not form_id:
        return jsonify({"error": "formdef_id is required"}), 400

    # Start the query to fetch category counts grouped by value
    query = (
        db.session.query(
            SurveyCategoryValue.category,
            SurveyCategoryValue.key,
            SurveyCategoryValue.value,
            func.count(SurveyCategoryValue.id).label('count')
        )
        .join(SurveyResponse, SurveyCategoryValue.survey_id == SurveyResponse.survey_id)
        .join(Survey, Survey.id == SurveyResponse.survey_id)
        .filter(Survey.formdef_id == form_id)
        .group_by(SurveyCategoryValue.category, SurveyCategoryValue.key, SurveyCategoryValue.value)
        .order_by(SurveyCategoryValue.category, SurveyCategoryValue.key, SurveyCategoryValue.value)
    )

    # Apply optional filters
    if category:
        query = query.filter(SurveyCategoryValue.category == category)
    if role:
        query = query.filter(SurveyResponse.role == role)

    # Execute the query
    results = query.all()

    # Map numeric values to labels
    value_labels = {
        "1": "Strongly Disagree",
        "2": "Disagree",
        "3": "Neutral",
        "4": "Agree",
        "5": "Strongly Agree"
    }

    # Function to replace long key names with Q1, Q2, etc.
    def replace_key_suffix(key):
        suffix = key.split('_')[-1]  # Extract the suffix (the last part after the underscore)
        try:
            suffix_num = int(suffix)  # Convert to integer
            return f"Q{suffix_num}"
        except ValueError:
            return key  # Return the original key if conversion fails

    # Format the result as a dictionary grouped by category, key, and value
    output = {}
    for category, key, value, count in results:
        if category not in output:
            output[category] = {}

        new_key = replace_key_suffix(key)  # Replace long key name with Q format

        if new_key not in output[category]:
            output[category][new_key] = {}

        # Replace numeric value with label
        label = value_labels.get(value, str(value))  # Default to the value if label not found
        output[category][new_key][label] = count

    return jsonify(output)


@api_bp.route("/api/category_scores", methods=["GET"])
def fetch_category_scores():
    formdef_id = request.args.get("formdef_id")

    if not formdef_id:
        return jsonify({"error": "formdef_id is required"}), 400

    # Build the query to count the entries by age, gender, disability, education, and appr_comm
    query = (
        db.session.query(
            SurveyResponse.age,
            SurveyResponse.gender,
            SurveyResponse.disability,
            SurveyResponse.education,
            SurveyResponse.appr_comm,
            SurveyResponse.org_category,
            SurveyResponse.onbehalf,
            func.count(SurveyResponse.id).label('count')
        )
        .join(Survey, Survey.id == SurveyResponse.survey_id)
        .filter(Survey.formdef_id == formdef_id)
        .group_by(SurveyResponse.age, SurveyResponse.gender, SurveyResponse.disability,
                  SurveyResponse.education, SurveyResponse.appr_comm, SurveyResponse.onbehalf,
                  SurveyResponse.org_category)
    )

    results = query.all()

    # Define the mapping for organization categories
    org_category_mapping = {
        "1": "Private",
        "2": "Public",
        "3": "Supplier/Contractor",
        "4": "NGO"
    }

    # Format the result into a dictionary by category
    data = {
        "Age": {},
        "Gender": {},
        "Disability Status": {},
        "Education Level": {},
        "Communication Channel": {},
        "Organization Type": {}
    }

    # Populate the data dictionary with the results
    for age, gender, disability, education, appr_comm, org_category, onbehalf, count in results:
        if age:
            data["Age"][age] = data["Age"].get(age, 0) + count
        if gender:
            data["Gender"][gender] = data["Gender"].get(gender, 0) + count
        if disability:
            data["Disability Status"][disability] = data["Disability Status"].get(disability, 0) + count
        if education:
            data["Education Level"][education] = data["Education Level"].get(education, 0) + count
        if appr_comm:
            data["Communication Channel"][appr_comm] = data["Communication Channel"].get(appr_comm, 0) + count

        # Handle organization type
        if org_category or onbehalf:
            org_category = org_category if org_category or org_category is not None else onbehalf
            org_label = org_category_mapping.get(org_category)
            data["Organization Type"][org_label] = data["Organization Type"].get(org_label, 0) + count

    # Convert the data dictionary into a list format for easier chart rendering
    final_data = {
        category: [{"key": key, "count": count} for key, count in values.items()]
        for category, values in data.items()
    }

    return jsonify(final_data)
