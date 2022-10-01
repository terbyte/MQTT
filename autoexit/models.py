from django.db import models

class timeindb(models.Model):	
	cardcode=models.CharField(max_length=20,null=True,blank=True)
	vehicle=models.CharField(max_length=20,null=True,blank=True)
	plate=models.CharField(max_length=20,null=True,blank=True)
	timein=models.DateTimeField(null=True,blank=True)
	operator=models.CharField(max_length=50,null=True,blank=True)
	pic=models.CharField(max_length=500,null=True,blank=True)
	pic2=models.CharField(max_length=500,null=True,blank=True)
	lane=models.CharField(max_length=50,null=True,blank=True)
	pc=models.CharField(max_length=50,null=True,blank=True)

class scanned_qr(models.Model):
	qrcode=models.CharField(max_length=500,null=True,blank=True)
	time_scanned=models.DateTimeField(null=True,blank=True)