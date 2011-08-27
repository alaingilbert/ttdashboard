from settings import PROD
def prod(request):
   return {'PROD': PROD}
