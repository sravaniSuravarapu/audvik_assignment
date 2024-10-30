from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)  
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField()

    def __str__(self):
        return f"{self.name} {self.id}"
