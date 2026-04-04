INSERT INTO shop_inventory (shop_id, item_id, stock, restock_amount, restock_interval, last_restock)
SELECT 1, 101, -1, 0, 3600, NOW()
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1
    FROM shop_inventory
    WHERE shop_id = 1 AND item_id = 101
);
