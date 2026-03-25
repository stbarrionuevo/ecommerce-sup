from django.contrib import admin
from .models import *

class VariacionInline(admin.StackedInline):
    model=Variacion
    extra=1

class ProductoAdmin(admin.ModelAdmin):
    inlines = [VariacionInline]

class OrdenAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha', 'metodo_pago', 'total_final', 'pagado')
    list_editable = ('pagado',) 
    list_filter = ('pagado', 'metodo_pago', 'fecha')

admin.site.register(Producto, ProductoAdmin)
admin.site.register(Orden, OrdenAdmin)
admin.site.register(OrderItem)
admin.site.register(Variacion)

#Uso: No sirven para "cargarlos" a la base de datos (eso ya lo hizo la migración). Sirven para hacerlos visibles en el panel de control.