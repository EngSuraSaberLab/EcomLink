from django.db import models
from django.utils.text import slugify


def _generate_unique_slug(instance, source_value, model_class):
    base_slug = slugify(source_value) or "item"
    slug = base_slug
    counter = 2

    while model_class.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug

class Category(models.Model):
    name=models.CharField(max_length=255 , unique=True)
    slug=models.SlugField(max_length=255, unique=True, blank=True)
    featured=models.BooleanField(default=False)
    order=models.IntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _generate_unique_slug(self, self.name, Category)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Author(models.Model):
    name=models.CharField(max_length=255)
    bio=models.TextField(null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    name=models.CharField(max_length=255)
    slug=models.SlugField(max_length=255, unique=True, blank=True)
    short_description=models.TextField(null=True)
    description=models.TextField()
    image=models.ImageField(upload_to='photos/%y/%m/%d')
    pdf_file=models.FileField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    featured=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    category=models.ForeignKey(Category, on_delete=models.PROTECT)
    author=models.ForeignKey(Author,on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _generate_unique_slug(self, self.name, Product)
        super().save(*args, **kwargs)
      
    def __str__(self):
        return self.name
    
class Order(models.Model):
    customer=models.JSONField(default=dict)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
      
    def __str__(self):
        return str(self.pk)

class OrderProduct(models.Model):
    order=models.ForeignKey(Order, on_delete=models.PROTECT)
    product=models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at=models.DateTimeField(auto_now_add=True)

class Slider(models.Model):
    title= models.CharField(max_length=255)
    subtitle=models.TextField(max_length=500)
    image=models.ImageField(null=True , upload_to='photos/%y/%m/%d')
    order=models.IntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)




    
    
    



