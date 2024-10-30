from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
import pandas as pd
from .models import Customer
from django.shortcuts import get_object_or_404

from .serializers import ImportSerializer
from .serializers import CreateCustomerSerializer
import re
from django.urls import reverse_lazy
from django.db import IntegrityError
from django.http import HttpResponse
from django.http import Http404
from django.views.generic import CreateView

def home(request):
    return HttpResponse("Hello")

def is_valid_phone_number(phone_number):
    if isinstance(phone_number, str):
        pattern = r'^\d{3}-\d{3}-\d{4}$'
        return re.match(pattern, phone_number)
    return False  

def is_valid_email(email):
    if isinstance(email, str):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email)
    return False 

class ImportAPIView(APIView):
    serializer_class = ImportSerializer
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            data = request.FILES
            serializer = self.serializer_class(data=data)
            
            #validate the file
            if not serializer.is_valid():
                return Response({
                    'status': False,
                    'message': 'Provide a valid file'
                }, status=status.HTTP_400_BAD_REQUEST)
             
            #readi the excel file 
            excel_file = data.get('file')
            try:
                #reads the first sheet of excel
                df = pd.read_excel(excel_file, sheet_name=0)
            except Exception as e:
                return Response({
                    'status': False,
                    'message': f'Invalid file format: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)

            required_columns = ['Name', 'Email', 'Phone Number', 'Address', 'Date of Birth']
            
            #check the all required files are present or not
            if not all(column in df.columns for column in required_columns):
                return Response({
                    'status': False,
                    'message': 'Missing required columns in the Excel file'
                }, status=status.HTTP_400_BAD_REQUEST)
           
            #initialize the lists to store customer objects and errors
            customers = []
            errors = []
            row_number = 1
            email_set = set() 

            for index, row in df.iterrows():
                name = row.get('Name')
                email = row.get('Email')
                phone_number = row.get('Phone Number')
                address = row.get('Address')
                date_of_birth = row.get('Date of Birth')

                row_errors = []
               
               #validating fields
                if not name or pd.isna(name):
                    row_errors.append("Name is required")
                if not email or pd.isna(email): 
                    row_errors.append("Email is required")

                if phone_number and not is_valid_phone_number(str(phone_number)):
                    row_errors.append("Invalid phone number format (e.g., 123-456-7890)")

                if email:
                    if not is_valid_email(str(email)):
                        row_errors.append("Invalid email format")
                    if email in email_set:
                        row_errors.append("Duplicate email in file")
                    else:
                        email_set.add(email)

                if email and Customer.objects.filter(email=email).exists():
                    row_errors.append("Customer with this email already exists")

                if row_errors:
                    errors.append({"row": row_number, "errors": row_errors})
                else:

                    #creating the customer object
                    customer = Customer(
                        name=name,
                        email=email,
                        phone_number=phone_number,
                        address=address,
                        date_of_birth=date_of_birth,
                    )
                    customers.append(customer)#adding to the list for bulk creation

                row_number += 1
   

           #create the customers
            if customers:
                try:
                    Customer.objects.bulk_create(customers)
                except IntegrityError as e:
                    errors.append({"error": str(e)})
            if errors:
                return Response({
                    'status': False,
                    'message': 'Some customers were not imported due to errors',
                    'errors': errors
                }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            return Response({
                'status': True,
                'message': 'Customers imported successfully!'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'status': False,
                'message': f'We could not complete the request: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


#display all records
class ListCustomersView(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CreateCustomerSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#create sutomer
class CreateAPIView(APIView):
    serializer_class = CreateCustomerSerializer

    def post(self, request):
        try:
            data = request.data
            serializer = self.serializer_class(data=data)

            if not serializer.is_valid():
                return Response({
                    'status': False,
                    'message': 'Invalid data provided',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            name = data.get('name')
            email = data.get('email')
            phone_number = data.get('phone_number')
            address = data.get('address')
            date_of_birth = data.get('date_of_birth')

            if Customer.objects.filter(email=email).exists():
                return Response({
                    'status': False,
                    'message': 'Customer with this email already exists'
                }, status=status.HTTP_400_BAD_REQUEST)

            customer = Customer(
                name=name,
                email=email,
                phone_number=phone_number,
                address=address,
                date_of_birth=date_of_birth
            )
            customer.save()

            return Response({
                'status': True,
                'message': 'Customer created successfully!'
            }, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            return Response({
                'status': False,
                'message': f'Integrity error: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'status': False,
                'message': f'We could not complete the request: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

#update
class UpdateAPIView(APIView):
    serializer_class = CreateCustomerSerializer

    def put(self, request, pk):
        try:
            customer = get_object_or_404(Customer, pk=pk)
            serializer = self.serializer_class(customer, data=request.data, partial=True)

            if not serializer.is_valid():
                return Response({
                    'status': False,
                    'message': 'Invalid data provided',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            email = request.data.get('email')
            if email and Customer.objects.filter(email=email).exclude(pk=pk).exists():
                return Response({
                    'status': False,
                    'message': 'Customer with this email already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

            return Response({
                'status': True,
                'message': 'Customer updated successfully!'
            }, status=status.HTTP_200_OK)

        except IntegrityError as e:
            return Response({
                'status': False,
                'message': f'Integrity error: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        except Customer.DoesNotExist:
            return Response({
                'status': False,
                'message': 'No Customer matches the given ID'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'status': False,
                'message': f'We could not complete the request: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
#delete
class DeleteAPIView(APIView):

    def delete(self, request, pk):
        try:
            customer = get_object_or_404(Customer, pk=pk)
            customer.delete()

            return Response({
                'status': True,
                'message': 'Customer deleted successfully!'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': False,
                'message': f'We could not complete the request: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)