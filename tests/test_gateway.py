from io import BytesIO
import base64
import unittest
from unittest.mock import patch

from PIL import Image
import requests
from ai.ollama import GatewayError, OllamaProvider, prepare_image


class GatewayTests(unittest.TestCase):
    def test_image_is_resized_and_encoded(self):
        image = BytesIO()
        Image.new("RGBA", (1600, 800), "red").save(image, format="PNG")
        with Image.open(BytesIO(base64.b64decode(prepare_image(image.getvalue())))) as result:
            self.assertEqual(result.size, (768, 384))
            self.assertEqual(result.mode, "RGB")
            self.assertEqual(result.format, "JPEG")

    def test_invalid_image(self):
        with self.assertRaises(GatewayError):
            prepare_image(b"not an image")

    @patch("ai.ollama.requests.post")
    def test_request_and_timings(self, post):
        post.return_value.__enter__.return_value.json.return_value = {
            "message": {"content": "Happy Halloween!"}, "done": True,
            "eval_duration": 250000000}
        result = OllamaProvider("http://test:11434").generate_text("Say hello")
        self.assertEqual(result.phrase, "Happy Halloween!")
        self.assertEqual(result.timings["ollama_eval_s"], 0.25)
        self.assertEqual(post.call_args.kwargs["timeout"], (5, 120))
        self.assertFalse(post.call_args.kwargs["json"]["stream"])

    @patch("ai.ollama.requests.post")
    def test_bad_responses(self, post):
        response = post.return_value.__enter__.return_value
        for data in ([], {}, {"error": "missing model"},
                     {"done": True, "message": {"content": ""}},
                     {"done": True, "done_reason": "length", "message": {"content": "Hello"}}):
            with self.subTest(data=data), self.assertRaises(GatewayError):
                response.json.return_value = data
                OllamaProvider("http://test").generate_text("Hello")

    @patch("ai.ollama.requests.post", side_effect=requests.Timeout)
    def test_timeout(self, post):
        with self.assertRaisesRegex(GatewayError, "timed out"):
            OllamaProvider("http://test").generate_text("Hello")

    @patch("ai.ollama.requests.post")
    def test_image_request(self, post):
        image = BytesIO()
        Image.new("RGB", (10, 10)).save(image, format="PNG")
        post.return_value.__enter__.return_value.json.return_value = {
            "done": True, "message": {"content": "That cape really lifts your spirits!"}}
        result = OllamaProvider("http://test").generate_halloween_line(image.getvalue())
        self.assertIn("images", post.call_args.kwargs["json"]["messages"][1])
        self.assertIn("image_prepare_s", result.timings)


if __name__ == "__main__":
    unittest.main()
