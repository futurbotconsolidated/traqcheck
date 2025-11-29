from rest_framework.renderers import JSONRenderer
from collections import defaultdict


class CustomJSONRenderer(JSONRenderer):
    def flatten_errors(self, errors):
        if isinstance(errors, list):
            flattened = []
            for error in errors:
                if isinstance(error, (dict, list)):
                    flattened.extend(self.flatten_errors(error))
                else:
                    flattened.append(str(error))
            return flattened
        elif isinstance(errors, dict):
            flattened = []
            for key, value in errors.items():
                flattened.extend(self.flatten_errors(value))
            return flattened
        else:
            return [str(errors)]

    def format_serializer_errors(self, data):
        formatted_errors = defaultdict(list)

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for field, errors in item.items():
                        flattened_errors = self.flatten_errors(errors)
                        formatted_errors[field].extend(flattened_errors)
        elif isinstance(data, dict):
            for field, errors in data.items():
                flattened_errors = self.flatten_errors(errors)
                formatted_errors[field] = " ".join(flattened_errors)

        return dict(formatted_errors)

    def get_first_error_message(self, errors):
        for field, message in errors.items():
            if isinstance(message, str):
                return message
            elif isinstance(message, list) and message:
                return message[0]
        return "An error occurred"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response', None)
        status_code = getattr(response, 'status_code', 200)

        if isinstance(data, dict):
            message = data.pop('detail', None)
        else:
            message = None

        if status_code >= 400:
            if isinstance(data, dict):
                formatted_errors = self.format_serializer_errors(data)
            else:
                formatted_errors = data

            first_error_message = self.get_first_error_message(
                formatted_errors if isinstance(formatted_errors, dict) else {}
            )

            error_data = {
                "message": message or first_error_message or "An error occurred",
                "errors": formatted_errors if isinstance(formatted_errors, dict) else None,
                "data": None,
                "status": "error",
                "status_code": status_code
            }
            return super().render(error_data, accepted_media_type, renderer_context)

        success_data = {
            "message": message or "Request successful",
            "errors": None,
            "data": data,
            "status": "success",
            "status_code": status_code
        }

        return super().render(success_data, accepted_media_type, renderer_context)
