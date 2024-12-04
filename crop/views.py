from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated  # Ensure this import is present
from django.shortcuts import get_object_or_404
from django.utils.timezone import now, timedelta
import cloudinary   
import cloudinary.uploader

from .models import Crop
from .serializers import * 
from account.models import User

from rest_framework.pagination import PageNumberPagination

class CropPagination(PageNumberPagination):
    page_size = 10  # Default number of items per page
    page_size_query_param = 'page_size'  # Allow clients to control the page size
    max_page_size = 50  # Limit the maximum page size

# Create your views here.

# Crops of a farmer
class CropList(APIView):
    serializer_class = CropSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        if user_id is None:
            crops = Crop.objects.all()
        else:
            crops = Crop.objects.filter(user_id=user_id)
        serializer = self.serializer_class(crops, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CropDetailsView(APIView):
    serializer_class = CropSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        crop = get_object_or_404(Crop, pk=pk)
        serializer = self.serializer_class(crop)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CropCreate(APIView):
    serializer_class = CropCreateSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        crops = Crop.objects.filter(user_id=request.user.id)
        serializer = self.serializer_class(crops, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        request.data['user'] = request.user.id  # Set the user id directly
        request.data['quantity_listed'] = request.data['quantity']  # Set the listed quantity to the total quantity
        image = request.FILES.get("image")

        image_url = None
        image_public_id = None
        if image:
            upload_result = cloudinary.uploader.upload(image, folder="crops")
            image_url = upload_result.get('url')
            image_public_id = upload_result.get('public_id')  # Get the public ID
            print("Uploaded image URL:", image_url)  # Print the URL for debugging
        
        request.data['image_url'] = image_url
        request.data['image_public_id'] = image_public_id


        serializer = self.serializer_class(data=request.data, context={'request': request})  # Pass context
        serializer.is_valid(raise_exception=True)
        try:
            crop = serializer.save()  # Save directly from the serializer
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
class CropDetails(APIView):
    serializer_class = CropSerializer
    permission_classes = [IsAuthenticated]
        
    def get_object(self, pk):
        return get_object_or_404(Crop, pk=pk, user=self.request.user)

    def get(self, request, pk):
        crop = self.get_object(pk)
        serializer = self.serializer_class(crop)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def put(self, request, pk):
    #     crop = self.get_object(pk)
    #     image = request.FILES.get("image")
    #     old_image_public_id = crop.image_public_id
        
    #     if image:
    #         upload_result = cloudinary.uploader.upload(image, folder="crops")
    #         image_url = upload_result.get('url')
    #         image_public_id = upload_result.get('public_id')

    #     request.data['image_url'] = image_url
    #     request.data['image_public_id'] = image_public_id
        
    #     # Delete the old image from Cloudinary
    #     if old_image_public_id:
    #         cloudinary.uploader.destroy(old_image_public_id)
        
    #     serializer = self.serializer_class(crop, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     try:
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        crop = self.get_object(pk)
        image = request.FILES.get("image")
        old_image_public_id = crop.image_public_id

        if image:
            upload_result = cloudinary.uploader.upload(image, folder="crops")
            image_url = upload_result.get('url')
            image_public_id = upload_result.get('public_id')
            request.data['image_url'] = image_url
            request.data['image_public_id'] = image_public_id
        
            # Delete the old image from Cloudinary
            if old_image_public_id:
                cloudinary.uploader.destroy(old_image_public_id)
 
        
        serializer = self.serializer_class(crop, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        crop = self.get_object(pk)

        # Delete the image from Cloudinary using the public ID
        if crop.image_public_id:
            cloudinary.uploader.destroy(crop.image_public_id)
            
        crop.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CropListByCategory(APIView):
    serializer_class = CropSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, category):
        crops = Crop.objects.filter(category=category)
        serializer = self.serializer_class(crops, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# class CropListByDiet(APIView):
#     serializer_class = CropSerializer
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request, diet):
#         crops = Crop.objects.filter(category=diet)
#         serializer = self.serializer_class(crops, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

class AddCropQuantity(APIView):
    serializer_class = CropSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        crop = get_object_or_404(Crop, pk=pk)
        if crop.user != request.user:
            return Response({'error': 'You do not have permission to add quantity to this crop'}, status=status.HTTP_403_FORBIDDEN)
        crop.quantity += request.data['quantity']
        # crop.quantity_listed += request.data['quantity']
        quantity = QuantityAdded.objects.create(crop=crop, quantity=request.data['quantity'])
        crop.save()
        serializer = self.serializer_class(crop)
        
        # Adjust the response to properly format the dictionary
        return Response({
            "crop": serializer.data,  # Crop data should be serialized
            "quantity_added": quantity.quantity,  # Return the added quantity
            "date_added": quantity.added_at # Include the date when the quantity was added (if needed)
        }, status=status.HTTP_200_OK)


class BuyCrop(APIView):
    serializer_class = SalesSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        crop = get_object_or_404(Crop, pk=pk)
        request.data["price_at_sale"] = crop.price*request.data["quantity_sold"]  # Calculating the total price

        # Passing the crop instance through context
        serializer = self.serializer_class(data=request.data, context={'crop': crop, 'request': request})

        if serializer.is_valid(raise_exception=True):
            try:
                sale = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except serializers.ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderedCrops(APIView):
    serializer_class = SalesSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sales = Sales.objects.filter(user=request.user)
        serializer = self.serializer_class(sales, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductSalesAnalysisView(APIView):
    serializer_class = CropSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, period):
        if period == '1day':
            time_threshold = now() - timedelta(days=1)
        elif period == '30days':
            time_threshold = now() - timedelta(days=30)
        elif period == '1year':
            time_threshold = now() - timedelta(days=365)
        else:
            return Response({"error": "Invalid period"}, status=status.HTTP_400_BAD_REQUEST)

        crops = Crop.objects.filter(user_id=request.user.id)
        sales = Sales.objects.filter(crop__user__id=request.user.id, sale_date__gte=time_threshold)

        # Total revenue and total sales for the time period
        total_revenue = sum(sale.price_at_sale for sale in sales)
        total_sales = sales.count()

        # Product listing with sales info
        product_sales = []
        for crop in crops:
            crop_sales = sales.filter(crop=crop)
            quantity_sold = sum(sale.quantity_sold for sale in crop_sales)

            # Calculate the total added quantity and total remaining quantity
            total_quantity_added = crop.quantity_added.aggregate(total=models.Sum('quantity'))['total'] or 0
            remaining_quantity = total_quantity_added - quantity_sold

            product_sales.append({
                "name": crop.name,
                "quantity_listed": total_quantity_added,
                "quantity_remaining": remaining_quantity,
                "price": crop.price,
                "quantity_sold": quantity_sold,
                "created_at": crop.created_at,
                "sales": [
                    {
                        "quantity_sold": sale.quantity_sold,
                        "price_at_sale": sale.price_at_sale,
                        "sale_date": sale.sale_date,
                    }
                    for sale in crop_sales
                ],
            })

        return Response({
            "total_revenue": total_revenue,
            "total_sales": total_sales,
            "product_sales": product_sales,
        })


class SearchRecommendations(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CropSerializer

    def get(self, request):
        user = request.user
        query = request.query_params.get('query')

        # Retrieve crops matching the query
        crops = Crop.objects.filter(name__icontains=query).distinct('name')
        serializer = self.serializer_class(crops, many=True)

        # Initialize `results` as a list to store recommendations
        results = []

        # Add crop recommendations
        for crop in crops:
            results.append({
                "name": crop.name,
                "source": "crop"
            })

        # Retrieve search history older than 30 days
        search_history = SearchHistory.objects.filter(user=user, search_query__icontains=query, search_date__gte=now() - timedelta(days=30)).distinct('search_query')
        for search in search_history:
            results.append({
                "name": search.search_query,
                "source": "searchHistory"
            })

        return Response(results, status=status.HTTP_200_OK)

class SearchCrops(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CropSerializer
    pagination_class = CropPagination


    def get(self, request):
        query = request.query_params.get('query', '').strip()
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        category = request.query_params.get('category', '').strip()

        # Validate and parse filter values
        filters = {}
        if min_price:
            try:
                filters['price__gte'] = float(min_price)
            except ValueError:
                return Response(
                    {"error": "Invalid value for min_price"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if max_price:
            try:
                filters['price__lte'] = float(max_price)
            except ValueError:
                return Response(
                    {"error": "Invalid value for max_price"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if category:
            filters['category'] = category

        # Query the database
        # TODO: if none field are defined the query goes undefinitly
        crops = Crop.objects.filter(name__icontains=query, **filters).order_by('name') if query else Crop.objects.filter(**filters).order_by('name')



        # Save search history only if there's a valid query
        if query != '':
            if not SearchHistory.objects.filter(user=request.user, search_query=query).exists():
                SearchHistory.objects.create(user=request.user, search_query=query)

        serializer = self.serializer_class(crops, many=True)
        
        # Apply pagination
        paginator = self.pagination_class()
        paginated_crops = paginator.paginate_queryset(crops, request)
        serializer = self.serializer_class(paginated_crops, many=True)
        return paginator.get_paginated_response(serializer.data )

        
class RateCrop(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RatingSerializer
    
    def get(self, request, pk):
        crop = get_object_or_404(Crop, pk=pk)
        ratings = Rating.objects.filter(crop=crop)
        serializer = self.serializer_class(ratings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        crop = get_object_or_404(Crop, pk=pk)
        request.data['crop'] = crop.id
        request.data['user'] = request.user.id
        image = request.FILES.get("image")

        image_url = None
        image_public_id = None
        if image:
            upload_result = cloudinary.uploader.upload(image, folder="crops-ratings")
            image_url = upload_result.get('url')
            image_public_id = upload_result.get('public_id')  # Get the public ID
            print("Uploaded image URL:", image_url)  # Print the URL for debugging
        
        request.data['image_url'] = image_url
        request.data['image_public_id'] = image_public_id

        serializer = self.serializer_class(data=request.data, context={'crop': crop, 'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RatingDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RatingSerializer
    
    def get(self, request, pk):
        rating = get_object_or_404(Rating, pk=pk)
        serializer = self.serializer_class(rating)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        rating = get_object_or_404(Rating, pk=pk)
        request.data['crop'] = rating.crop.id

        if rating.user != request.user:
            return Response({'error': 'You do not have permission to edit this rating'}, status=status.HTTP_403_FORBIDDEN)
        
        image = request.FILES.get("image")
        
        old_image_public_id = rating.image_public_id

        if image:
            upload_result = cloudinary.uploader.upload(image, folder="crops-ratings")
            image_url = upload_result.get('url')
            image_public_id = upload_result.get('public_id')
            request.data['image'] = image_url
            request.data['image_public_id'] = image_public_id

            # Delete the old image from Cloudinary
            if old_image_public_id:
                cloudinary.uploader.destroy(old_image_public_id)
            
            
        serializer = self.serializer_class(rating, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        rating = get_object_or_404(Rating, pk=pk)

        if rating.user != request.user:
            return Response({'error': 'You do not have permission to delete this rating'}, status=status.HTTP_403_FORBIDDEN)

        # Delete the image from Cloudinary using the public ID
        if rating.image_public_id:
            cloudinary.uploader.destroy(rating.image_public_id)
            
        rating.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)