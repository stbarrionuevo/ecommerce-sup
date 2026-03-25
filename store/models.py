from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
        nombre = models.CharField(max_length=200)
        imagen = models.ImageField(null=True,blank=True)
        precio = models.DecimalField(max_digits=10, decimal_places=2)
        fecha = models.DateTimeField(auto_now_add=True)
        categoria = models.CharField(max_length=25 , default="Suplemento")
        es_digital = models.BooleanField(default=False)

        def __str__(self):
                return self.nombre


class Variacion(models.Model):
       producto = models.ForeignKey(Producto,on_delete=models.CASCADE, related_name="variaciones")
       atributo = models.CharField(max_length=50, default="sabor")
       valor = models.CharField(max_length=50)
       stock = models.IntegerField(default=0)
       def __str__(self):
                return f"{self.producto.nombre} - {self.valor}"

class Orden(models.Model):
        usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
        fecha = models.DateTimeField(auto_now_add=True)
        completado = models.BooleanField(default=False)
        pagado = models.BooleanField(default=False)
        
        tipo_de_envio = models.CharField(max_length=30, default="Retiro en Local")
        costo_de_envio = models.DecimalField(max_digits=10,decimal_places=2,default=0)
        metodo_pago = models.CharField(max_length=50, default="Efectivo")
        @property
        def precio_total(self):
            items = self.orderitem_set.all()
            return sum([item.total for item in items])
        @property
        def total_final(self):
               return self.precio_total + self.costo_de_envio
        
class OrderItem(models.Model):
       producto = models.ForeignKey(Producto, on_delete=models.SET_NULL,null=True)
       orden = models.ForeignKey(Orden, on_delete=models.SET_NULL,null=True)
       cantidad = models.IntegerField(default=0)
       variacion = models.ForeignKey(Variacion, on_delete=models.SET_NULL, null=True,blank=True)
       @property
       def total(self):
              return self.producto.precio * self.cantidad


