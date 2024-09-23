import random
import string


def generate_vm_name(model):
    """
    example of generated codes: VMCY7UHJ2,VMCBCU68T
    """
    vm_initials = "VMC"
    numbers = "".join(random.sample(string.digits, k=2))
    lowercase_letters = "".join(random.choices(string.ascii_lowercase, k=4))
    final_string = numbers + lowercase_letters
    shuffled_string = "".join(random.sample(final_string, len(final_string)))
    code = vm_initials + shuffled_string

    if model.objects.filter(name=code).exists():
        code = generate_vm_name(model)

    return code.upper()
