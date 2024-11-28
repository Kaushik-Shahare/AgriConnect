from django.db import models

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} '

class CartItems(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='cart_items')
    crop = models.ForeignKey('crop.Crop', on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.crop}'