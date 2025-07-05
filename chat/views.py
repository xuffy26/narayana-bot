from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json
import re
import traceback

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
            print("RESPONSE STATUS:", response.status_code)
            print("RESPONSE RAW:", response.content)

            decoded_data = response.json()

            if response.status_code == 200:
                patient_list = []

                # Check both 'message_content' and 'body'
                message = decoded_data.get("message_content") or decoded_data.get("body", "")
                if message:
                    cleaned_msg = re.sub(r'\s+', ' ', message).strip()
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

                if patient_list:
                    return Response(patient_list, status=status.HTTP_200_OK)

            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
