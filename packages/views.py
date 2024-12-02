from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Package, Days, BookedPackage
from .serializers import PackageSerializer, DaysSerializer ,BookedPackageSerializer
from rest_framework.permissions import IsAuthenticated
from admin_user.jwtAuthentication import CustomJWTAuthentication
from django.shortcuts import get_object_or_404

class PackageView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]
    
    print('package view')
    def get(self, request, pk=None):
        print(request.data)
        """Handles GET requests."""
        if pk:
            # Retrieve a specific package
            package = get_object_or_404(Package, pk=pk)
            serializer = PackageSerializer(package)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # List all packages
            packages = Package.objects.all()
            serializer = PackageSerializer(packages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Handles POST requests."""
        serializer = PackageSerializer(data=request.data)
        if serializer.is_valid():
            package = serializer.save()

            # Process 'day_plans' if provided
            day_plans = request.data.get('day_plans', [])
            for day in day_plans:
                day["package"] = package.id
                day_serializer = DaysSerializer(data=day)
                if day_serializer.is_valid():
                    day_serializer.save()
                else:
                    return Response(day_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """Handles PUT requests."""
        package = get_object_or_404(Package, pk=pk)
        serializer = PackageSerializer(package, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Handles DELETE requests."""
        package = get_object_or_404(Package, pk=pk)

        # Check for related entries before deletion
        if Days.objects.filter(package=package).exists():
            return Response(
                {"error": "Cannot delete package as it is referenced in other tables."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        package.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookedPackageView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        """Handles GET requests."""
        if pk:
            # Retrieve a specific booking
            booking = get_object_or_404(BookedPackage, pk=pk)
            serializer = BookedPackageSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # List all bookings
            bookings = BookedPackage.objects.all()
            serializer = BookedPackageSerializer(bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Handles POST requests (create a new booking)."""
        data = request.data

        # Retrieve the associated package and calculate total_amount
        package = get_object_or_404(Package, id=data.get('package'))
        total_amount = (package.adult_price * data.get('adult_count', 0)) + \
                       (package.child_price * data.get('child_count', 0))
        data['total_amount'] = total_amount
        data['paid_amount'] = total_amount  # Assume the user paid the full amount

        serializer = BookedPackageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """Handles PUT requests (update a booking)."""
        booking = get_object_or_404(BookedPackage, pk=pk)
        serializer = BookedPackageSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Handles DELETE requests (delete a booking)."""
        booking = get_object_or_404(BookedPackage, pk=pk)
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)