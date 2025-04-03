from machado.models import History

def createAndSaveHistory(user, method, description, status):
    """
    Create and save a history object for a given user.
    """
    history = History.objects.create(
        user=user,
        method=method,
        description=description,
        status=status
    )

    return history