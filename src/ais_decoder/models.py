"""Data models and validators"""
from abc import ABC
from typing import Union, Any

from datetime import datetime
import re

class ValidationError(Exception): # pylint: disable=C0115
    pass


class Validator(ABC): # pylint: disable=R0903
    """
    Use regex to validate data

    :param accept:  raw regex to search for
    :param deny: regex that cannot be in the string

    :param data: validated string
    """
    accept: str = ""
    deny: Union[str, None] = None

    def __set_name__(self, owner, name):
        self.private_name = "_" + name

    def __get__(self, instance: Any, owner: type) -> Any:
        return getattr(instance, self.private_name)

    def __set__(self, instance: Any, value: str):
        """Run validators"""
        # optional, leave the default
        accept = bool(re.compile(self.accept).search(value))

        deny = True
        if self.deny is not None:
            deny = not re.compile(self.deny).search(value)

        if accept and deny:
            setattr(instance, self.private_name, value)
        else:
            raise ValidationError(f"{value} is invalid for field {self.private_name}")

class MsgTypeValidator(Validator): # pylint: disable=R0903
    """Accept only messages like '!ABCD'"""
    accept = r"^(!|\$)[A-Z]+$"

class DigitValidator(Validator): # pylint: disable=R0903
    """Accept only digits"""
    accept = r"^[0-9]$"

class DigitOrEmptyValidator(Validator): # pylint: disable=R0903
    """Accept digits or an empty string (for the secuential id message, an optional field)"""
    accept = r"^([0-9]|)$"

class AlphanumOrEmptyValidator(Validator): # pylint: disable=R0903
    """Accept only single letters, a digit or empty"""
    accept = r"^([A-Z0-9]|)$"

class PayloadValidator(Validator): # pylint: disable=R0903
    """Accept only ascii characters. From the space to tilde"""
    accept = r"^[ -~]+$"

class CheckSumValidator(Validator): # pylint: disable=R0903
    """ Fill bits * checksum."""
    accept = r"^[0-9]\*[A-Z0-9]{2}$"

class NMEASentence: #pylint: disable=R0902,R0903
    """NMEA sentence class. It validates a raw string and """
    # numerical fields could be coerced to string if needed
    msg_type: str = MsgTypeValidator()
    num_fragments: str = DigitValidator()
    num_fragment: str = DigitValidator()
    id_msg: str = DigitOrEmptyValidator()
    radio_channel: str = AlphanumOrEmptyValidator()
    payload: str = PayloadValidator()
    checksum: str = CheckSumValidator()

    # data fields
    __fields__ = (
        "msg_type",
        "num_fragments",
        "num_fragment",
        "id_msg",
        "radio_channel",
        "payload",
        "checksum"
    )

    def __init__(self, msg: str):
        msg = msg.strip()
        # exclude the checksum and the field delimiters
        msg_len = len(msg.replace(",", "")[:-2])
        if msg_len > 82:
            raise ValidationError(f"Message too long. It must not be longer than 82, got {msg_len}\n{msg}")
        chunks = msg.split(",")
        try:
            self.msg_type, self.num_fragments, self.num_fragment, self.id_msg, self.radio_channel, self.payload, self.checksum = chunks # pylint: disable=C0301
        except ValueError as exc:
            raise ValidationError(f"Too many/few fields. Expected 7, got {len(chunks)}. {chunks}") from exc
        self.timestamp: datetime = datetime.now()

    def __str__(self):
        rep = ""
        for val in self.__fields__:
            try:
                rep += getattr(self, val)
            except AttributeError:
                # not set yet, validation error
                rep += "Not-Set"
            if "*" not in val:
                # not last
                rep += ","
        return rep
