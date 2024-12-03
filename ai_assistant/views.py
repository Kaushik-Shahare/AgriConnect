from django.shortcuts import render
from AgriConnect.settings import GOOGLE_GEMINI_API_KEY
from rest_framework.views import APIView
from rest_framework.response import Response
import google.generativeai as genai

# Configure the API key for Google Gemini
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)

class AiAssistantView(APIView):
    def get(self, request):

        query = request.query_params.get("query")
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

        # Generate content using the AI model
        response = model.generate_content(
            # "Assume that you are a expert in the field of agriculture and a diet expert. You are asked to provide a detailed explanation on the following topic: " + query
            "Assume that you are a expert in the field of agriculture and a diet expert. Give answer to following question: " + query
        )

        # Return the Markdown content as part of the JSON response
        return Response({"markdown": response.text})