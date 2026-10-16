"""Project-level views (error handlers)."""

from django.http import JsonResponse


def not_found_handler(request, exception):
    """Renvoie un 404 JSON propre au lieu de la page HTML Django.

    Utile pour cette API JSON-only : un client qui tape une URL inexistante
    reçoit un payload cohérent (``{"detail": "Not found."}``) au lieu d'une
    page HTML. Avec ``DEBUG=False``, Django servirait sa page 404 par défaut
    (vide) ; avec ``DEBUG=True`` il listerait TOUTES les URL patterns du
    projet — fuite d'info. Ce handler coupe la fuite dans les deux cas.
    """
    return JsonResponse({"detail": "Not found."}, status=404)
