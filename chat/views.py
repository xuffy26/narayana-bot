from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json
import re

class CheckPatientChat(APIView):

    def post(self, request):
        try:
            user_number = request.data.get("user_number")
            query = request.data.get("query")
            mobile_prefix = request.data.get("mobile_prefix")
            basic_url_endpoint = request.data.get("basic_url_endpoint")

            url = f"{basic_url_endpoint}/api/chat"

            payload = json.dumps({
                "user_number": user_number,
                "message": query,
                "mobile_prefix": mobile_prefix
            })

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(url, headers=headers, data=payload)
            decoded_data = response.json()

            if response.status_code == 200:
                # Prepare patient list with dynamic message_content as body
                patient_list = []

                message_content = decoded_data.get("message_content", "").strip()
                if message_content:
                    # Clean up whitespace
                    cleaned_msg = re.sub(r'\s+', ' ', message_content)
                    patient_list.append({"body": cleaned_msg})

                if "sections" in decoded_data and isinstance(decoded_data["sections"], list):
                    for section in decoded_data["sections"]:
                        rows = section.get("rows", [])
                        for row in rows:
                            patient_list.append({
                                "id": row.get("id"),
                                "title": row.get("title"),
                                "description": row.get("description")
                            })

                # Return either the list or a fallback
                if patient_list:
                    return Response(patient_list, status=status.HTTP_200_OK)

            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
