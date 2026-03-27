-- Run this once to enable the MySQL event scheduler.
-- This lets MySQL automatically clean up expired reaction trigger rows.
-- You only need to run this one time ever.
SET GLOBAL event_scheduler = ON;
