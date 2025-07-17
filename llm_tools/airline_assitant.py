#!/usr/bin/env python3


# There's a particular dictionary structure that's required to describe our function:
definiton = {
    "name": "get_ticket_price",

    "description": "Get the price of a return ticket to the destination city. Call this " + \
        "whenever you need to know the ticket price, for example when a customer asks " + \
        "'How much is a ticket to this city'",

    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The city that the customer wants to travel to",
            },
        },
        "required": ["destination_city"],
        "additionalProperties": False,
    }
}

def assistant(destination_city):
    #print(f"<-- get_ticket_price: {destination_city}")
    ticket_prices = {
        "london": "$799",
        "paris": "$899",
        "tokyo": "$1400",
        "berlin": "$499",
    }

    price = ticket_prices.get(destination_city.lower(), "unknown")

    return { "destination_city": destination_city, "price": price }
