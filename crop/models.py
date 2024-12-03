from django.db import models

# Create your models here.

crop_catogory = [
    ('vegetable', 'Vegetable'),
    ('fruit', 'Fruit'),
    ('cereal', 'Cereal'),
    ('grain', 'Grain'),
    ('dairy', 'Dairy'),
    ('meat', 'Meat'),
    ('poultry', 'Poultry'),
    ('seafood', 'Seafood'),
    ('herb', 'Herb'),
    ('spice', 'Spice'),
    ('other', 'Other'),
]

class Crop(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='crops')
    name = models.CharField(max_length=255)
    image_url = models.URLField(blank=True, null=True)  
    image_public_id = models.CharField(max_length=255, blank=True, null=True)  
    description = models.TextField()
    category = models.CharField(choices=crop_catogory)
    quantity = models.IntegerField()
    # quantity_listed = models.IntegerField()
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class QuantityAdded(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='quantity_added')
    quantity = models.IntegerField()
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.quantity}kg added on {self.added_at}'

class Sales(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='sales')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='sales')
    quantity_sold = models.IntegerField()
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.crop.name} - {self.quantity_sold}kg sold on {self.sale_date}'

class SearchHistory(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='search_history')
    search_query = models.CharField(max_length=255)
    search_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.search_query} searched on {self.search_date}'