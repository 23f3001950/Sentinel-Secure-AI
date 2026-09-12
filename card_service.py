import requests


BIN_API_URL = "https://lookup.binlist.net"


def mask_card(card_number):
    card_number = str(card_number).replace(" ", "").replace("-", "")

    if len(card_number) <= 4:
        return "*" * len(card_number)

    return "*" * (len(card_number) - 4) + card_number[-4:]


def luhn_check(card_number):
    card_number = str(card_number).replace(" ", "").replace("-", "")

    if not card_number.isdigit():
        return False

    total = 0
    reverse_digits = card_number[::-1]

    for i, digit in enumerate(reverse_digits):
        number = int(digit)

        if i % 2 == 1:
            number *= 2

            if number > 9:
                number -= 9

        total += number

    return total % 10 == 0


def get_bin_info(card_number):
    card_number = str(card_number).replace(" ", "").replace("-", "")

    if len(card_number) < 6 or not card_number.isdigit():
        return {
            "success": False,
            "message": "Enter a valid card number."
        }

    if not luhn_check(card_number):
        return {
            "success": False,
            "message": "Card number failed Luhn validation."
        }

    bin_number = card_number[:6]

    try:
        response = requests.get(
            f"{BIN_API_URL}/{bin_number}",
            timeout=10,
            headers={"Accept-Version": "3"}
        )

        if response.status_code != 200:
            return {
                "success": False,
                "message": "Unable to retrieve BIN information."
            }

        data = response.json()

        bank = data.get("bank") or {}
        country = data.get("country") or {}
        number = data.get("number") or {}
        card_type = data.get("type") or "Unknown"

        return {
            "success": True,
            "card": mask_card(card_number),
            "bin": bin_number,
            "scheme": data.get("scheme", "Unknown").upper(),
            "type": card_type.capitalize(),
            "brand": data.get("brand", "Unknown"),
            "prepaid": data.get("prepaid", "Unknown"),
            "bank": bank.get("name", "Unknown"),
            "country": country.get("name", "Unknown"),
            "country_code": country.get("alpha2", "Unknown"),
            "currency": country.get("currency", "Unknown"),
            "numeric": number.get("length", "Unknown"),
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "BIN lookup timed out. Please try again."
        }

    except requests.exceptions.RequestException:
        return {
            "success": False,
            "message": "Network error while contacting BIN service."
        }

    except ValueError:
        return {
            "success": False,
            "message": "Invalid response received from BIN service."
        }