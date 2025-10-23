# from abc import ABC, abstractmethod
# from datetime import datetime, timezone
# from typing import List, Optional


# from ..models import db, Notification, BroadcastSubscription


# # -------- Interfaces --------
# class IObserver(ABC):
#     @abstractmethod
#     def update(self, cc: str, fulfilment_rate: float, description: str) -> None:
#         """Receive a broadcast event."""
#         pass

# class ISubject(ABC):
#     @abstractmethod
#     def register(self, observer: IObserver) -> None: ...


#     @abstractmethod
#     def unregister(self, observer: IObserver) -> None: ...


#     @abstractmethod
#     def notify(self, cc: str, fulfilment_rate: float, description: str) -> None: ...


# # -------- Concrete Observer --------
# class DBNotificationObserver(IObserver):
#     """Writes one Notification per *subscribed* user for the given CC."""
#     def update(self, cc: str, fulfilment_rate: float, description: str) -> None:
#         # Find all active subscribers to this CC
#         subs: List[BroadcastSubscription] = (
#         BroadcastSubscription.query.filter_by(cc=cc, active=True).all()
#         )
#         if not subs:
#             return
        
#         message = f"⚠️ {cc}: {description}"
#         now = datetime.now(timezone.utc)
#         try:
#             for s in subs:
#                 db.session.add(Notification(
#                 receiver_email=s.email,
#                 message=message,
#                 link=None,
#                 is_read=False,
#                 created_at=now,
#                 ))
#             db.session.commit()
#         except Exception:
#             db.session.rollback()
#             raise

# # -------- Concrete Subject (singleton-ish) --------
# class CCFulfilmentSubject(ISubject):
#     def __init__(self, threshold: float = 0.5):
#         self._observers: List[IObserver] = []
#         self.threshold = threshold
        

#     def register(self, observer: IObserver) -> None:
#         if observer not in self._observers:
#             self._observers.append(observer)


#     def unregister(self, observer: IObserver) -> None:
#         if observer in self._observers:
#             self._observers.remove(observer)

#     def notify(self, cc: str, fulfilment_rate: float, description: str) -> None:
#         for obs in list(self._observers):
#             obs.update(cc, fulfilment_rate, description)

#     # Helper: invoked by business logic
#     def maybe_broadcast(self, cc: str, fulfilment_rate: float) -> None:
#         if fulfilment_rate < self.threshold:
#             desc = (
#             "{fulfilment_rate:.0%} \ nBelow target: consider promoting donations or adjusting requests. "
#             "(Matched+Completed) / (Matched+Completed+Pending) < 50%.".format(fulfilment_rate)
#             )
#             self.notify(cc, fulfilment_rate, desc)

    

# # global, ready to use
# subject = CCFulfilmentSubject()
# subject.register(DBNotificationObserver())

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import List, Optional

from ..models import db, Notification

# ---------- Interfaces ----------
class IObserver(ABC):
    @abstractmethod
    def update(self, cc: str) -> None:
        """Called by Subject. Observer should PULL details from Subject."""
        raise NotImplementedError

class ISubject(ABC):
    @abstractmethod
    def register(self, observer: IObserver) -> None: ...

    @abstractmethod
    def unregister(self, observer: IObserver) -> None: ...


    @abstractmethod
    def notify(self, cc: str) -> None: ...


    @abstractmethod
    def set_desc(self, desc: str) -> None: ...


    @abstractmethod
    def get_desc(self, cc: str) -> Optional[str]: ...

# ---------- Concrete Observer ----------
@dataclass(eq=True, frozen=True)
class SubscriptionObserver(IObserver):
    """
    Represents ONE subscription (user_email + cc).
    Uses pull model: when update() is called, it pulls subject.get_desc(cc).
    """
    user_email: str
    cc: str
    _subject: "CCFulfilmentSubject"

    def update(self, cc: str) -> None:
        if cc != self.cc:
            return # ignore broadcasts for other CCs
        desc = self._subject.get_desc(cc) or ""
        # Create a Notification for this user
        now = datetime.now(timezone.utc)
        msg = f"⚠️ {self.cc}: {desc}"
        try:
            db.session.add(Notification(
                receiver_email=self.user_email,
                message=msg[:255],
                link=None,
                is_read=False,
                created_at=now,
            ))
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

# ---------- Concrete Subject ----------
class CCFulfilmentSubject(ISubject):
    """
    Keeps in‑memory list of SubscriptionObserver.
    Uses pull model: stores self.desc; observers pull with get_desc().


    Thread‑safe with a simple RLock. Suitable for single‑process Flask.
    """
    def __init__(self, threshold: float = 0.5):
        self._lock = RLock()
        self._observers: List[SubscriptionObserver] = []
        self.threshold = threshold
        self.desc: Optional[str] = None # last broadcast description

    # --- ISubject impl ---
    def register(self, observer: SubscriptionObserver) -> None:
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)

    def unregister(self, observer: SubscriptionObserver) -> None:
        with self._lock:
            try:
                self._observers.remove(observer)
            except ValueError:
                pass

    def notify(self, cc: str) -> None:
    # copy snapshot to avoid mutation issues while iterating
        with self._lock:
            observers = list(self._observers)
        for obs in observers:
            if isinstance(obs, SubscriptionObserver) and obs.cc == cc:
                obs.update(cc)

    def set_desc(self, desc: str) -> None:
        self.desc = desc

    def get_desc(self, cc: str) -> Optional[str]:
        # For now, desc is global. If you want per‑CC history, change to a dict.
        return self.desc

    # --- Utilities for routes ---
    def find(self, user_email: str, cc: str) -> Optional[SubscriptionObserver]:
        with self._lock:
            for o in self._observers:
                if o.user_email == user_email and o.cc == cc:
                    return o
        return None

    def subscriptions_for_user(self, user_email: str) -> List[SubscriptionObserver]:
        with self._lock:
            return [o for o in self._observers if o.user_email == user_email]

    # --- Business helper invoked by metrics ---
    def maybe_broadcast(self, cc: str, fulfilment_rate: float) -> None:
        if fulfilment_rate < self.threshold:
            # Compose a friendly description (what observers will PULL)
            self.set_desc(
                (
                    f"Fulfilment rate is {fulfilment_rate:.0%}. "
                    "Below target: Your donation is needed!"
                )
            )
            self.notify(cc)
    
subject = CCFulfilmentSubject()