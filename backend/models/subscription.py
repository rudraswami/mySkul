"""
Subscription and payment-related models for Dhruv AI application
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid


class SubscriptionPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # free, basic, premium, pro
    display_name: str
    price_monthly: float = 0.0
    price_yearly: float = 0.0
    stripe_price_monthly: Optional[str] = None
    stripe_price_yearly: Optional[str] = None
    features: List[str] = []
    limits: Dict[str, int] = {}  # feature_name: limit_value
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserSubscription(BaseModel):
    subscription_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    plan_id: str
    plan_name: str  # free, basic, premium, pro
    status: str = "active"  # active, cancelled, expired, paused
    billing_cycle: str = "monthly"  # monthly, yearly
    current_period_start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    current_period_end: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=30))
    stripe_subscription_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    auto_renew: bool = True
    trial_end: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PaymentTransaction(BaseModel):
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subscription_id: Optional[str] = None
    amount: float
    currency: str = "INR"
    payment_method: str = "stripe"
    stripe_session_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    status: str = "initiated"  # initiated, pending, completed, failed, cancelled, refunded
    payment_status: str = "unpaid"  # unpaid, paid, failed
    description: str
    metadata: Dict[str, Any] = {}
    invoice_number: Optional[str] = None
    gst_amount: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Razorpay Models
class RazorpayOrderCreate(BaseModel):
    amount: int  # Amount in paise (INR)
    currency: str = "INR"
    plan_name: str  # FREE, PREMIUM, PRO
    billing_cycle: str = "monthly"  # monthly, yearly
    user_id: str


class RazorpayOrderResponse(BaseModel):
    order_id: str
    amount: int
    currency: str
    key_id: str
    plan_name: str
    billing_cycle: str


class RazorpayPaymentSuccess(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    user_id: str


class RazorpaySubscription(BaseModel):
    subscription_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    plan_name: str  # FREE, PREMIUM, PRO
    billing_cycle: str = "monthly"
    amount: int  # Amount in paise
    status: str = "created"  # created, paid, failed, cancelled
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=30))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UsageTracking(BaseModel):
    usage_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    feature_name: str  # ai_conversations, mock_tests, audio_processing
    usage_count: int = 0
    usage_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reset_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(day=1) + timedelta(days=32))


# Request/Response Models
class SubscriptionRequest(BaseModel):
    plan_name: str
    billing_cycle: str = "monthly"  # monthly, yearly


class FeatureAccessRequest(BaseModel):
    feature_name: str


class CheckoutRequest(BaseModel):
    plan_name: str
    billing_cycle: str = "monthly"
    success_url: str
    cancel_url: str