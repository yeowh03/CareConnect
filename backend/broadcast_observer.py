"""Broadcast Observer Service for CareConnect Backend.

This module implements the Observer pattern for broadcasting
low fulfillment rate notifications to subscribed users.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import List, Optional

from .models import db, Notification
from .services.notification_strategies import DatabaseNotificationStrategy

class IObserver(ABC):
    """Observer interface for the Observer pattern."""
    @abstractmethod
    def update(self, cc: str) -> None:
        """Called by Subject when notification needed.
        
        Args:
            cc (str): Community club name.
        """
        raise NotImplementedError
    
    @abstractmethod
    def is_interested_in(self, cc: str) -> bool:
        """Check if observer is interested in this CC.
        
        Args:
            cc (str): Community club name.
            
        Returns:
            bool: True if interested in notifications for this CC.
        """

class ISubject(ABC):
    """Subject interface for the Observer pattern."""
    @abstractmethod
    def register(self, observer: IObserver) -> None:
        """Register an observer.
        
        Args:
            observer (IObserver): Observer to register.
        """

    @abstractmethod
    def unregister(self, observer: IObserver) -> None:
        """Unregister an observer.
        
        Args:
            observer (IObserver): Observer to unregister.
        """


    @abstractmethod
    def notify(self, cc: str) -> None:
        """Notify all interested observers.
        
        Args:
            cc (str): Community club name.
        """


    @abstractmethod
    def set_desc(self, desc: str) -> None: ...


    @abstractmethod
    def get_desc(self, cc: str) -> Optional[str]: ...

# ---------- Concrete Observer ----------
@dataclass(eq=True, frozen=True)
class SubscriptionObserver(IObserver):
    """Observer for user subscription to CC broadcasts.
    
    Represents ONE subscription (user_email + cc).
    Uses pull model: when update() is called, it pulls subject.get_desc(cc).
    """
    user_email: str
    cc: str
    _subject : ISubject
    _notification_strategy: DatabaseNotificationStrategy = DatabaseNotificationStrategy()

    def update(self, cc: str) -> None:
        # Only process notifications for subscribed CC
        if cc != self.cc:
            return # ignore broadcasts for other CCs
        
        # Pull the latest description from subject (pull model)
        desc = self._subject.get_desc(cc) or ""
        
        # Create notification for this user
        now = datetime.now(timezone.utc)
        msg = f"⚠️ {self.cc}: {desc}"
        try:
            self._notification_strategy.create_notification(msg, self.user_email)
        except Exception:
            db.session.rollback()
            raise

    def is_interested_in(self, cc):
        return self.cc == cc

# ---------- Concrete Subject ----------
class CCFulfilmentSubject(ISubject):
    """Subject for CC fulfillment rate broadcasts.
    
    Keeps in‑memory list of SubscriptionObserver.
    Uses pull model: stores self.desc; observers pull with get_desc().
    Thread‑safe with a simple RLock. Suitable for single‑process Flask.
    """
    def __init__(self, threshold: float = 0.5):
        self._lock = RLock()
        self._observers: List[IObserver] = []
        self.threshold = threshold
        self.desc: Optional[str] = None # last broadcast description

    # --- ISubject impl ---
    def register(self, observer: IObserver) -> None:
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)

    def unregister(self, observer: IObserver) -> None:
        with self._lock:
            try:
                self._observers.remove(observer)
            except ValueError:
                pass

    def notify(self, cc: str) -> None:
        # Create snapshot of observers to avoid mutation issues during iteration
        with self._lock:
            observers = list(self._observers)
        
        # Notify all observers interested in this CC
        for obs in observers:
            if obs.is_interested_in(cc):
                obs.update(cc)

    def set_desc(self, desc: str) -> None:
        self.desc = desc

    def get_desc(self, cc: str) -> Optional[str]:
        # For now, desc is global. If you want per‑CC history, change to a dict.
        return self.desc

    # --- Utilities for routes ---
    def find(self, user_email: str, cc: str) -> Optional[IObserver]:
        with self._lock:
            for o in self._observers:
                if o.user_email == user_email and o.cc == cc:
                    return o
        return None

    def subscriptions_for_user(self, user_email: str) -> List[IObserver]:
        with self._lock:
            return [o for o in self._observers if o.user_email == user_email]

    # --- Business helper invoked by metrics ---
    def maybe_broadcast(self, cc: str, fulfilment_rate: float) -> None:
        """Broadcast if fulfillment rate is below threshold.
        
        Args:
            cc (str): Community club name.
            fulfilment_rate (float): Current fulfillment rate (0.0 to 1.0).
        """
        # Only broadcast if fulfillment rate is below threshold (default 50%)
        if fulfilment_rate < self.threshold:
            # Set description that observers will pull when notified
            self.set_desc(
                (
                    f"Fulfilment rate is {fulfilment_rate:.0%}. "
                    "Below target: Your donation is needed!"
                )
            )
            # Notify all observers subscribed to this CC
            self.notify(cc)
    
subject = CCFulfilmentSubject()