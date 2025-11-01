# backend/services/notification_strategies.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from ..models import Notification, User, db


class NotificationStrategy(ABC):
    """Abstract base class for notification strategies"""
    
    @abstractmethod
    def send_notification(self, message: str, recipients: List[str], **kwargs) -> Dict[str, Any]:
        """Send notification to recipients"""
        pass
    
    @abstractmethod
    def format_message(self, template: str, data: Dict[str, Any]) -> str:
        """Format message using template and data"""
        pass


class DatabaseNotificationStrategy(NotificationStrategy):
    """Store notifications in database for individual users"""
    
    def send_notification(self, message: str, recipients: List[str], **kwargs) -> Dict[str, Any]:
        """Store notification in database"""
        try:
            notifications = []
            for recipient in recipients:
                # Validate recipient exists
                user = User.query.get(recipient)
                if not user:
                    continue
                
                notif = Notification(
                    message=message,
                    receiver_email=recipient,
                    created_at=datetime.now(timezone.utc)
                )
                db.session.add(notif)
                notifications.append(notif)
            
            db.session.commit()
            
            return {
                "success": True,
                "strategy": "database",
                "sent_count": len(notifications),
                "notification_ids": [n.id for n in notifications]
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "strategy": "database",
                "error": str(e),
                "sent_count": 0
            }
    
    def format_message(self, template: str, data: Dict[str, Any]) -> str:
        """Simple string formatting for database notifications"""
        try:
            return template.format(**data)
        except KeyError as e:
            return f"Template error: Missing key {e}"


class BroadcastNotificationStrategy(NotificationStrategy):
    """Broadcast notifications to multiple users via observer pattern"""
    
    def __init__(self, subject=None):
        from .broadcast_observer import subject as default_subject
        self.subject = subject or default_subject
    
    def send_notification(self, message: str, recipients: List[str], **kwargs) -> Dict[str, Any]:
        """Broadcast notification via observer pattern"""
        try:
            cc = kwargs.get("cc")
            if not cc:
                return {
                    "success": False,
                    "strategy": "broadcast",
                    "error": "Community center (cc) required for broadcast",
                    "sent_count": 0
                }
            
            # Set the broadcast message
            self.subject.set_desc(message)
            
            # Notify all observers for this CC
            self.subject.notify(cc)
            
            # Count subscribers for this CC
            subscriber_count = len([
                obs for obs in self.subject._observers 
                if obs.is_interested_in(cc)
            ])
            
            return {
                "success": True,
                "strategy": "broadcast",
                "cc": cc,
                "subscriber_count": subscriber_count,
                "sent_count": subscriber_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "strategy": "broadcast",
                "error": str(e),
                "sent_count": 0
            }
    
    def format_message(self, template: str, data: Dict[str, Any]) -> str:
        """Format broadcast messages with emoji and urgency"""
        try:
            formatted = template.format(**data)
            urgency = data.get("urgency", "normal")
            
            if urgency == "high":
                return f"🚨 URGENT: {formatted}"
            elif urgency == "medium":
                return f"⚠️ {formatted}"
            else:
                return f"ℹ️ {formatted}"
                
        except KeyError as e:
            return f"Template error: Missing key {e}"


class EmailNotificationStrategy(NotificationStrategy):
    """Send notifications via email (mock implementation)"""
    
    def __init__(self, smtp_config: Optional[Dict[str, Any]] = None):
        self.smtp_config = smtp_config or {}
    
    def send_notification(self, message: str, recipients: List[str], **kwargs) -> Dict[str, Any]:
        """Send email notifications (mock implementation)"""
        try:
            subject = kwargs.get("subject", "CareConnect Notification")
            
            # Mock email sending - in real implementation, use SMTP
            sent_emails = []
            for recipient in recipients:
                # Validate email format
                if "@" not in recipient:
                    continue
                
                # Mock email sending
                email_data = {
                    "to": recipient,
                    "subject": subject,
                    "body": message,
                    "sent_at": datetime.now(timezone.utc).isoformat()
                }
                sent_emails.append(email_data)
            
            return {
                "success": True,
                "strategy": "email",
                "sent_count": len(sent_emails),
                "emails": sent_emails
            }
            
        except Exception as e:
            return {
                "success": False,
                "strategy": "email",
                "error": str(e),
                "sent_count": 0
            }
    
    def format_message(self, template: str, data: Dict[str, Any]) -> str:
        """Format email messages with HTML support"""
        try:
            formatted = template.format(**data)
            
            # Add HTML formatting for emails
            if data.get("html", False):
                return f"<html><body><p>{formatted}</p></body></html>"
            
            return formatted
            
        except KeyError as e:
            return f"Template error: Missing key {e}"


class SMSNotificationStrategy(NotificationStrategy):
    """Send notifications via SMS (mock implementation)"""
    
    def __init__(self, sms_config: Optional[Dict[str, Any]] = None):
        self.sms_config = sms_config or {}
    
    def send_notification(self, message: str, recipients: List[str], **kwargs) -> Dict[str, Any]:
        """Send SMS notifications (mock implementation)"""
        try:
            # Truncate message for SMS
            sms_message = message[:160] + "..." if len(message) > 160 else message
            
            sent_sms = []
            for recipient in recipients:
                # Validate phone number format (simplified)
                if not recipient.startswith("+"):
                    continue
                
                # Mock SMS sending
                sms_data = {
                    "to": recipient,
                    "message": sms_message,
                    "sent_at": datetime.now(timezone.utc).isoformat()
                }
                sent_sms.append(sms_data)
            
            return {
                "success": True,
                "strategy": "sms",
                "sent_count": len(sent_sms),
                "messages": sent_sms
            }
            
        except Exception as e:
            return {
                "success": False,
                "strategy": "sms",
                "error": str(e),
                "sent_count": 0
            }
    
    def format_message(self, template: str, data: Dict[str, Any]) -> str:
        """Format SMS messages (keep short)"""
        try:
            formatted = template.format(**data)
            # Truncate for SMS
            return formatted[:160] + "..." if len(formatted) > 160 else formatted
            
        except KeyError as e:
            return f"Template error: Missing key {e}"


class MultiChannelNotificationStrategy(NotificationStrategy):
    """Send notifications through multiple channels"""
    
    def __init__(self, strategies: List[NotificationStrategy]):
        self.strategies = strategies
    
    def send_notification(self, message: str, recipients: List[str], **kwargs) -> Dict[str, Any]:
        """Send notification through all configured strategies"""
        results = []
        total_sent = 0
        
        for strategy in self.strategies:
            result = strategy.send_notification(message, recipients, **kwargs)
            results.append(result)
            if result.get("success"):
                total_sent += result.get("sent_count", 0)
        
        return {
            "success": any(r.get("success") for r in results),
            "strategy": "multi_channel",
            "total_sent": total_sent,
            "channel_results": results
        }
    
    def format_message(self, template: str, data: Dict[str, Any]) -> str:
        """Use first strategy's formatting"""
        if self.strategies:
            return self.strategies[0].format_message(template, data)
        return template.format(**data)


class NotificationContext:
    """Context class that uses notification strategies"""
    
    def __init__(self):
        self._strategy: Optional[NotificationStrategy] = None
    
    def set_strategy(self, strategy: NotificationStrategy):
        """Set the notification strategy"""
        self._strategy = strategy
    
    def send_notification(self, message: str, recipients: List[str], **kwargs) -> Dict[str, Any]:
        """Send notification using current strategy"""
        if not self._strategy:
            return {
                "success": False,
                "error": "No notification strategy set",
                "sent_count": 0
            }
        
        return self._strategy.send_notification(message, recipients, **kwargs)
    
    def send_formatted_notification(self, template: str, data: Dict[str, Any], 
                                  recipients: List[str], **kwargs) -> Dict[str, Any]:
        """Send notification with formatted message"""
        if not self._strategy:
            return {
                "success": False,
                "error": "No notification strategy set",
                "sent_count": 0
            }
        
        formatted_message = self._strategy.format_message(template, data)
        return self._strategy.send_notification(formatted_message, recipients, **kwargs)