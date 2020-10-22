from services.RoomReservation.ConfigManager import ConfigManager
from services.RoomReservation.libbureauactif.db.DBManager import DBManager


redis_client = None
api_user_token_key = None

TokenCookieName = 'RoomReservationToken'
config_man = ConfigManager()

# Database manager
db_man = DBManager()

# OpenTera com manager
service_opentera = None

