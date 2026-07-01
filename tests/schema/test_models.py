from app.models import ChatResponse, HealthResponse, Recommendation


def test_health_schema():
    model = HealthResponse()
    assert model.model_dump() == {"status": "ok"}


def test_chat_response_schema():
    response = ChatResponse(
        reply="Hello",
        recommendations=[
            Recommendation(
                name="OPQ32r",
                url="https://www.shl.com/products/product-catalog/view/opq/",
                test_type="P",
            )
        ],
        end_of_conversation=False,
    )
    payload = response.model_dump()
    assert payload["reply"] == "Hello"
    assert payload["recommendations"][0]["test_type"] == "P"
