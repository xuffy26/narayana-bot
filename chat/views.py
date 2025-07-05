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
                final_list = []

                # Get the greeting message
                message_content = decoded_data.get("message_content", "").strip()
                cleaned_msg = re.sub(r'\s+', ' ', message_content) if message_content else ""

                # Get the rows
                rows = []
                if "sections" in decoded_data and isinstance(decoded_data["sections"], list):
                    for section in decoded_data["sections"]:
                        rows = section.get("rows", [])
                        break  # Only first section considered

                # Add first row with body
                if cleaned_msg and rows:
                    first_row = rows[0]
                    final_list.append({
                        "body": cleaned_msg,
                        "id": first_row.get("id"),
                        "title": first_row.get("title"),
                        "description": first_row.get("description")
                    })

                    # Add remaining rows (without body)
                    for row in rows[1:]:
                        final_list.append({
                            "id": row.get("id"),
                            "title": row.get("title"),
                            "description": row.get("description")
                        })

                    return Response(final_list, status=status.HTTP_200_OK)

            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
