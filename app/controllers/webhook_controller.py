from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.models.models import Survey, SurveyResponse, SurveyCategoryValue, db

webhook_bp = Blueprint("webhook", __name__)


@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        if not data:
            raise ValueError("No JSON data received")
        print("Received data:", data)

        # Process and structure data
        processed_data = {}

        def update_dict_with_prefix(existing_dict, key, value):
            # Extract the prefix from the key
            prefix = key.split("_")[0]

            # If the key has a suffix (_1, _2, etc.), handle it as a grouped field
            if "_" in key and key.split("_")[-1].isdigit():
                if prefix in existing_dict:
                    # Ensure that the group exists as a dictionary and append the value
                    if isinstance(existing_dict[prefix], dict):
                        existing_dict[prefix][key] = value
                    else:
                        # If the existing entry is not a dict, convert it into a dict with the new key-value pair
                        existing_dict[prefix] = {key: value}
                else:
                    # Create the group with the current key-value pair
                    existing_dict[prefix] = {key: value}
            else:
                # If no suffix, just add the key-value pair as a simple field
                existing_dict[key] = value

        for key, value in data.items():
            update_dict_with_prefix(processed_data, key, value)

        print("Processed data:", processed_data)

        # Check for duplicate entry
        existing_survey = Survey.query.filter_by(instanceID=processed_data.get("instanceID")).first()
        if existing_survey:
            return jsonify({"status": "duplicate", "message": "Record already exists"}), 200

        # Insert the survey
        survey = Survey(
            formdef_version=processed_data.get("formdef_version"),
            formdef_id=processed_data.get("formdef_id"),
            instanceID=processed_data.get("instanceID"),
            key=processed_data.get("KEY"),
            submission_url=processed_data.get("submission_url"),
            submissionDate=datetime.strptime(
                processed_data.get("SubmissionDate", "1970-01-01T00:00:00.000Z"),
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        )
        db.session.add(survey)
        db.session.flush()  # Get survey.id before committing

        # Insert survey responses
        response = SurveyResponse(
            survey_id=survey.id,
            appr_comm=processed_data.get("appr_comm"),
            other_appr_comm=processed_data.get("other_appr_comm"),
            kippra_interaction=processed_data.get("kippra_interaction"),
            start_interaction=processed_data.get("start_interaction"),
            overall_satisfaction=processed_data.get("overall_satisfaction"),
            like_most_abt_kippra=processed_data.get("like_most_abt_kippra"),
            not_like_abt_kippra=processed_data.get("not_like_abt_kippra"),
            as_ceo_advice=processed_data.get("as_ceo_advice"),
            suggestions=processed_data.get("suggestions"),
            gender=processed_data.get("gender"),
            age=processed_data.get("age"),
            disability=processed_data.get("disability"),
            disability_true=bool(processed_data.get("disability_true", False)),
            education=processed_data.get("education"),
            other_education=processed_data.get("other_education"),
            kwldg_abt_kippra=processed_data.get("kwldg_abt_kippra"),
            respondents_name=processed_data.get("respondents_name"),
            org_name=processed_data.get("org_name"),
            org_category=processed_data.get("org_category"),
            role=processed_data.get("org_role"),
            onbehalf=processed_data.get("onbehalf"),
            note24=processed_data.get("note24"),
            note25=processed_data.get("note25")
        )
        db.session.add(response)

        # Define a mapping for category replacements
        category_replacements = {
            "prod": "products and services",
            "accessability": "Accessibility",
            "communication": "Communication",
            "complaints": "complaints handling",
            "service": "Satisfaction with services",
            "product": "Satisfaction with Products",
            "image": "Image/Identity",
            "delivery": "Service Delivery",
            "procurement": "Procurement (Suppliers only)",
            "channel": "Dissemination channels",
        }

        # Insert category values
        for category, values in processed_data.items():
            if isinstance(values, dict):  # Only handle grouped fields
                # Replace the category name using the mapping
                category_replaced = category_replacements.get(category,
                                                              category)

                for key, value in values.items():
                    category_value = SurveyCategoryValue(
                        survey_id=survey.id,
                        category=category_replaced,
                        key=key,
                        value=value
                    )
                    db.session.add(category_value)

        db.session.commit()

        return jsonify({"status": "success", "processed_data": processed_data}), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Database integrity error"}), 400

    except Exception as e:
        db.session.rollback()
        print(f"Error processing data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400
