import re
import json
from rest_framework.parsers import JSONParser

class LenientJSONParser(JSONParser):
    """
    JSON parser that strips trailing commas before loading.
    """
    def parse(self, stream, media_type=None, parser_context=None):
        raw = stream.read().decode('utf-8')
        cleaned = re.sub(r',\s*}', '}', raw)
        cleaned = re.sub(r',\s*\]', ']', cleaned)
        return json.loads(cleaned)