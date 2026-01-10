from django.db import models
from django.utils import timezone
from datetime import date
from calendar import monthrange


class PaymentPeriod(models.Model):
    """Represents a payment period for Daniel's royalties."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('due', 'Due'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]
    
    # The book product name to track
    BOOK_PRODUCT_NAME = "Through Bear's Eyes"
    
    start_date = models.DateField()
    end_date = models.DateField()
    amount_per_book = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        unique_together = ['start_date', 'end_date']
    
    def __str__(self):
        return f"{self.period_name} - £{self.total_amount}"
    
    @property
    def period_name(self):
        """Generate a human-readable period name."""
        if self.start_date.day == 16 and self.start_date.month == 12 and self.start_date.year == 2025:
            return "December 2025 (Launch)"
        return self.start_date.strftime("%B %Y")
    
    @property
    def books_sold(self):
        """Calculate books sold from orders in this period."""
        from orders.models import LineItem
        from django.db.models import Sum
        from datetime import datetime, timedelta
        
        # Convert dates to datetime for proper filtering
        start_datetime = datetime.combine(self.start_date, datetime.min.time())
        # End date should include the entire day
        end_datetime = datetime.combine(self.end_date + timedelta(days=1), datetime.min.time())
        
        # Make datetimes timezone-aware
        from django.utils import timezone as tz
        start_datetime = tz.make_aware(start_datetime)
        end_datetime = tz.make_aware(end_datetime)
        
        # Count all "Through Bear's Eyes" books sold in this period
        # Use order_date (original Shopify date) instead of created_at (import date)
        result = LineItem.objects.filter(
            product_name__icontains="Through Bear's Eyes",
            order__order_date__gte=start_datetime,
            order__order_date__lt=end_datetime
        ).aggregate(total=Sum('quantity'))
        
        return result['total'] or 0
    
    @property
    def total_amount(self):
        """Calculate total amount owed for this period."""
        return self.books_sold * self.amount_per_book
    
    @property
    def is_overdue(self):
        """Check if payment is overdue."""
        if self.status == 'paid':
            return False
        return date.today() > self.payment_due_date
    
    def update_status(self):
        """Update the status based on current date and payment state."""
        today = date.today()
        
        if self.paid_date:
            self.status = 'paid'
        elif today > self.payment_due_date:
            self.status = 'overdue'
        elif today > self.end_date:
            self.status = 'due'
        else:
            self.status = 'pending'
        self.save()
    
    @classmethod
    def get_or_create_current_periods(cls):
        """Create payment periods from launch date to current month."""
        from datetime import date
        from calendar import monthrange
        
        periods_created = []
        
        # Start from December 2025 (launch month)
        launch_date = date(2025, 12, 16)
        today = date.today()
        
        # December 2025 - special case (16th - 31st)
        dec_2025_start = date(2025, 12, 16)
        dec_2025_end = date(2025, 12, 31)
        dec_2025_due = date(2026, 2, 28)  # Due by end of February 2026
        
        period, created = cls.objects.get_or_create(
            start_date=dec_2025_start,
            end_date=dec_2025_end,
            defaults={
                'payment_due_date': dec_2025_due,
                'status': 'pending'
            }
        )
        if created:
            periods_created.append(period)
        
        # Generate monthly periods from January 2026 onwards
        current_year = 2026
        current_month = 1
        
        while date(current_year, current_month, 1) <= today:
            # Get last day of month
            _, last_day = monthrange(current_year, current_month)
            
            period_start = date(current_year, current_month, 1)
            period_end = date(current_year, current_month, last_day)
            
            # Due date is last day of the month after next (2 months later)
            # e.g., January 2026 is due by end of March 2026
            due_month = current_month + 2
            due_year = current_year
            if due_month > 12:
                due_month -= 12
                due_year += 1
            _, due_last_day = monthrange(due_year, due_month)
            payment_due = date(due_year, due_month, due_last_day)
            
            period, created = cls.objects.get_or_create(
                start_date=period_start,
                end_date=period_end,
                defaults={
                    'payment_due_date': payment_due,
                    'status': 'pending'
                }
            )
            if created:
                periods_created.append(period)
            
            # Move to next month
            if current_month == 12:
                current_year += 1
                current_month = 1
            else:
                current_month += 1
        
        # Update statuses for all periods
        for period in cls.objects.all():
            period.update_status()
        
        return periods_created
