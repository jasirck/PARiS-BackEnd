from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Resort, ResortImages, ResortCategory, BookedResort
from .serializers import (
    ResortSerializer,
    ResortImageSerializer,
    UserResortSerializer,
    CategorySerializer,
    BookedResortSerializer,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from admin_user.jwtAuthentication import (
    CustomJWTAuthentication,
    CustomAdminJWTAuthentication,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404


class ResortView(APIView):
    def get(self, request):
        resorts = Resort.objects.filter(valid=True).prefetch_related("images").all()
        serializer = UserResortSerializer(resorts, many=True)
        return Response(serializer.data)


class ResortDetailView(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    def get(self, request, pk):
        print("pk", pk)
        try:
            resort = Resort.objects.get(id=pk)
            print(resort)
            serializer = ResortSerializer(resort)
            return Response(serializer.data)
        except Resort.DoesNotExist:

            return Response(
                {"error": "Resort not found"}, status=status.HTTP_404_NOT_FOUND
            )


class AdminResortView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, resort_id=None):
        if resort_id:
            try:
                resort = Resort.objects.get(id=resort_id)
                serializer = ResortSerializer(resort)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Resort.DoesNotExist:
                return Response(
                    {"error": "Resort not found"}, status=status.HTTP_404_NOT_FOUND
                )
        resorts = Resort.objects.all().order_by("name")
        serializer = ResortSerializer(resorts, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        print(request.data)
        mutable_data = request.data.copy()
        images = mutable_data.pop("images", None)

        serializer = ResortSerializer(data=mutable_data)
        if serializer.is_valid():
            resort = serializer.save()

            if images:
                image_list = images[0].split(",")
                for image_url in image_list:
                    ResortImages.objects.create(resort=resort, image=image_url)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        resort_id = kwargs.get("resort_id")
        try:
            resort = Resort.objects.get(id=resort_id)
        except Resort.DoesNotExist:
            return Response(
                {"error": "Resort not found"}, status=status.HTTP_404_NOT_FOUND
            )
        mutable_data = request.data.copy()
        images = mutable_data.pop("images", None)
        serializer = ResortSerializer(resort, data=mutable_data)
        if serializer.is_valid():
            updated_resort = serializer.save()
            if images:
                ResortImages.objects.filter(resort=resort).delete()
                image_list = images.split(",")
                for image_url in image_list:
                    ResortImages.objects.create(resort=updated_resort, image=image_url)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookedResortView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        package = get_object_or_404(Resort, id=data.get("resort"))
        total_amount = (package.adult_price * data.get("adults", 0)) + (
            package.child_price * data.get("children", 0)
        ) * data.get("days")
        data["total_amount"] = total_amount
        data["paid_amount"] = 0
        data["user"] = user.id
        serializer = BookedResortSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        print(request.user)
        if pk:
            booking = get_object_or_404(BookedResort, pk=pk)
            serializer = BookedResortSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # List all bookings
            bookings = BookedResort.objects.filter(user=request.user).order_by(
                "-created_at"
            )
            serializer = BookedResortSerializer(bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class AdminBookedResortView(APIView):
    authentication_classes = [CustomAdminJWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            # Retrieve a specific booking
            booking = get_object_or_404(BookedResort, pk=pk)
            serializer = BookedResortSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # List all bookings
            bookings = BookedResort.objects.all()
            print(bookings)
            bookings = BookedResort.objects.all().order_by(
                "-start_date"
            )  # Order before serialization
            serializer = BookedResortSerializer(bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        booking_id = request.data.get("id")
        status_value = request.data.get("status")

        try:
            booking = BookedResort.objects.get(id=booking_id)
            booking.conformed = status_value
            booking.save()
            return Response(
                {"message": "Booking status updated successfully"},
                status=status.HTTP_200_OK,
            )
        except BookedResort.DoesNotExist:
            return Response(
                {"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        booking = get_object_or_404(BookedResort, pk=pk)
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminResortImageView(APIView):
    def post(self, request, resort_id):
        try:
            resort = Resort.objects.get(id=resort_id)
        except Resort.DoesNotExist:
            return Response(
                {"error": "Resort not found"}, status=status.HTTP_404_NOT_FOUND
            )
        print(request.data)
        serializer = ResortImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(resort=resort)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, pk=None):
        if pk:
            try:
                category = ResortCategory.objects.get(pk=pk)
            except ResortCategory.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        else:
            categories = ResortCategory.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        if pk:
            try:
                category = ResortCategory.objects.get(pk=pk)
            except ResortCategory.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

            serializer = CategorySerializer(
                category, data=request.data, partial=True
            )  # Partial update
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            category = ResortCategory.objects.get(id=pk)
            category.delete()
            return Response(
                {"message": "Category deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except ResortCategory.DoesNotExist:
            return Response(
                {"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND
            )


class CategoryShowView(APIView):
    def get(
        self,
        request,
    ):
        categories = ResortCategory.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


from django.views.decorators.csrf import csrf_exempt
from cloudinary.uploader import destroy
from django.http import JsonResponse


def delete_image(request):
    if request.method == "POST":
        import json

        data = json.loads(request.body)
        public_id = data.get("public_id")

        if not public_id:
            return JsonResponse({"error": "public_id is required"}, status=400)

        try:
            result = destroy(public_id)
            if result.get("result") == "ok":
                return JsonResponse(result, status=200)
            else:
                return JsonResponse(
                    {"error": "Failed to delete image", "details": result}, status=400
                )
        except Exception as e:
            return JsonResponse(
                {"error": "Cloudinary error", "details": str(e)}, status=500
            )
