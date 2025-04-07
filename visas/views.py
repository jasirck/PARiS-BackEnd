from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from .models import VisaCategory, Visa, VisaDays, VisaBooked
from .serializers import (
    VisaCategorySerializer,
    VisaSerializer,
    VisaDaysSerializer,
    GetVisaSerializer,
    VisaBookedSerializer,
    AdminBookedVisaSerializer,
)
from admin_user.jwtAuthentication import CustomJWTAuthentication
from rest_framework.utils.serializer_helpers import ReturnDict


# Helper function to get object or raise NotFound error
def get_object_or_404(model, pk):
    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        raise NotFound(detail=f"{model.__name__} not found", code=404)


class CategoryShowView(APIView):
    """Fetch all visa categories."""

    def get(self, request):
        categories = VisaCategory.objects.all()
        serializer = VisaCategorySerializer(categories, many=True)
        return Response(serializer.data)


class VisaCategoryListCreateView(APIView):
    """List and create visa categories."""

    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request):
        categories = VisaCategory.objects.all()
        serializer = VisaCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = VisaCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VisaCategoryDetailView(APIView):
    """Retrieve, update or delete a specific visa category."""

    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, pk):
        category = get_object_or_404(VisaCategory, pk)
        serializer = VisaCategorySerializer(category)
        return Response(serializer.data)

    def patch(self, request, pk):
        category = get_object_or_404(VisaCategory, pk)
        serializer = VisaCategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = get_object_or_404(VisaCategory, pk)
        category.delete()
        return Response(
            {"message": "Category deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class VisaListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        visas = Visa.objects.all().order_by("name")
        serializer = GetVisaSerializer(visas, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Log the incoming request to see if data is being passed correctly
        print("Request data received:", request.data)

        visa_data = request.data
        visa_days_data = visa_data.pop("visa_days", [])

        visa_serializer = VisaSerializer(data=visa_data)
        if visa_serializer.is_valid():
            visa = visa_serializer.save()

            # Process each visa_day item
            for visa_day_data in visa_days_data:
                visa_day_data["visa"] = visa.id
                visa_day_serializer = VisaDaysSerializer(data=visa_day_data)
                if visa_day_serializer.is_valid():
                    visa_day_serializer.save()
                else:
                    print(
                        f"Visa day {visa_day_data} failed validation: {visa_day_serializer.errors}"
                    )
                    return Response(
                        visa_day_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(visa_serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Visa serializer errors:", visa_serializer.errors)
            return Response(visa_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VisaDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        print("pk", pk)
        visa = get_object_or_404(Visa, pk)
        serializer = GetVisaSerializer(visa)
        return Response(serializer.data)

    def put(self, request, pk):
        # Log the incoming request to see if data is being passed correctly (Use logging in production)
        print("Request data received:", request.data)

        visa_data = request.data
        visa_days_data = visa_data.pop("visa_days", [])

        try:
            # Fetch the existing visa by ID
            visa = Visa.objects.get(id=pk)
        except Visa.DoesNotExist:
            return Response(
                {"detail": "Visa not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Update the visa instance with new data
        visa_serializer = VisaSerializer(
            visa, data=visa_data, partial=True
        )  # Use partial=True to allow partial updates
        if visa_serializer.is_valid():
            visa_serializer.save()

            # Delete existing visa days before saving the new ones
            VisaDays.objects.filter(visa=visa).delete()

            # Process each visa_day item
            for visa_day_data in visa_days_data:
                visa_day_data["visa"] = visa.id
                visa_day_serializer = VisaDaysSerializer(data=visa_day_data)
                if visa_day_serializer.is_valid():
                    visa_day_serializer.save()
                else:
                    # Log detailed error and return
                    print(
                        f"Visa day {visa_day_data} failed validation: {visa_day_serializer.errors}"
                    )
                    return Response(
                        visa_day_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(visa_serializer.data, status=status.HTTP_200_OK)
        else:
            # Return the errors if the Visa serializer is invalid
            print(f"Visa update failed validation: {visa_serializer.errors}")
            return Response(visa_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        visa = get_object_or_404(Visa, pk)
        visa.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VisaDaysListCreateView(APIView):
    """List and create visa days."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        visa_days = VisaDays.objects.all()
        serializer = VisaDaysSerializer(visa_days, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = VisaDaysSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VisaDaysDetailView(APIView):
    """Retrieve, update or delete a specific visa day."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        visa_day = get_object_or_404(VisaDays, pk)
        serializer = VisaDaysSerializer(visa_day)
        return Response(serializer.data)

    def put(self, request, pk):
        visa_day = get_object_or_404(VisaDays, pk)
        serializer = VisaDaysSerializer(visa_day, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        visa_day = get_object_or_404(VisaDays, pk)
        visa_day.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VisaVisaDaysView(APIView):
    """Get all visa days related to a specific visa."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        visa = get_object_or_404(Visa, pk)
        visa_days = VisaDays.objects.filter(visa=visa)
        serializer = VisaDaysSerializer(visa_days, many=True)
        return Response(serializer.data)


class BookedVisaView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request):
        visas = VisaBooked.objects.filter(user=request.user.id).order_by("-created_at")
        serializer = VisaBookedSerializer(visas, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()

        # Map the incoming 'user_id' and 'days_id' to 'user' and 'days'
        data["user"] = request.user.id  # Map user_id to user

        print(data)

        serializer = AdminBookedVisaSerializer(data=data)
        print(serializer.is_valid())
        print(serializer.errors)

        if serializer.is_valid():
            booked_visa = serializer.save()
            return Response(
                AdminBookedVisaSerializer(booked_visa).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminBookedVisaAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch all VisaBooked entries
        visa_bookings = VisaBooked.objects.all().order_by("-created_at")
        serializer = VisaBookedSerializer(visa_bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Handle approval or decline
        visa_booking_id = request.data.get("id")
        status_value = request.data.get("status")

        if not visa_booking_id or status_value not in ["Approved", "Declined"]:
            return Response(
                {"detail": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            visa_booking = VisaBooked.objects.get(id=visa_booking_id)
            visa_booking.conformed = status_value
            visa_booking.save()

            return Response(
                {"detail": f"Visa request {status_value.lower()} successfully."},
                status=status.HTTP_200_OK,  # Corrected here to use `status.HTTP_200_OK`
            )
        except VisaBooked.DoesNotExist:
            return Response(
                {"detail": "Visa booking not found."}, status=status.HTTP_404_NOT_FOUND
            )
