def clamp(number, min_v, max_v):
    if number < min_v:
        return min_v
    elif number > max_v:
        return max_v
    else:
        return number


def moveTowards(current, target, amount):
    if current < target:
        return min(current + amount, target)
    else:
        return max(current - amount, target)


def moveTowards(current, target, amountUp, amountDown):
    if current < target:
        return min(current + amountUp, target)
    else:
        return max(current - amountDown, target)
