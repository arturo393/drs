select * from  icinga_host;
+----+-------------------+-------------+----------+--------------+-------------------+----------+------------------+--------------------+-----------------+----------------+----------------+---------------+----------------------+----------------------+-----------------------+----------------------+-----------------+-----------------+------------------+-------------------------+------------------------+----------+---------+---------------------+-------+-----------+------------+------------+----------------+-----------+-----------------------+---------------+---------+--------------------+
| id | object_name       | object_type | disabled | display_name | address           | address6 | check_command_id | max_check_attempts | check_period_id | check_interval | retry_interval | check_timeout | enable_notifications | enable_active_checks | enable_passive_checks | enable_event_handler | enable_flapping | enable_perfdata | event_command_id | flapping_threshold_high | flapping_threshold_low | volatile | zone_id | command_endpoint_id | notes | notes_url | action_url | icon_image | icon_image_alt | has_agent | master_should_connect | accept_config | api_key | template_choice_id |
+----+-------------------+-------------+----------+--------------+-------------------+----------+------------------+--------------------+-----------------+----------------+----------------+---------------+----------------------+----------------------+-----------------------+----------------------+-----------------+-----------------+------------------+-------------------------+------------------------+----------+---------+---------------------+-------+-----------+------------+------------+----------------+-----------+-----------------------+---------------+---------+--------------------+
|  6 | host_template     | template    | n        | NULL         | NULL              | NULL     |              168 |               NULL |            NULL | NULL           | NULL           |          NULL | NULL                 | NULL                 | NULL                  | NULL                 | NULL            | NULL            |             NULL |                    NULL |                   NULL | NULL     |    NULL |                NULL | NULL  | NULL      | NULL       | NULL       | NULL           | NULL      | NULL                  | NULL          | NULL    |               NULL |
|  7 | google.com        | object      | n        | NULL         | google.com        | NULL     |             NULL |               NULL |            NULL | NULL           | NULL           |          NULL | NULL                 | NULL                 | NULL                  | NULL                 | NULL            | NULL            |             NULL |                    NULL |                   NULL | NULL     |    NULL |                NULL | NULL  | NULL      | NULL       | NULL       | NULL           | NULL      | NULL                  | NULL          | NULL    |               NULL |
|  8 | sigma-telecom.com | object      | n        | NULL         | sigma-telecom.com | NULL     |             NULL |               NULL |            NULL | NULL           | NULL           |          NULL | NULL                 | NULL                 | NULL                  | NULL                 | NULL            | NULL            |             NULL |                    NULL |                   NULL | NULL     |    NULL |                NULL | NULL  | NULL      | NULL       | NULL       | NULL           | NULL      | NULL                  | NULL          | NULL    |               NULL |
|  9 | Yahoo             | object      | n        | NULL         | yahoo.com         | NULL     |             NULL |               NULL |            NULL | NULL           | NULL           |          NULL | NULL                 | NULL                 | NULL                  | NULL                 | NULL            | NULL            |             NULL |                    NULL |                   NULL | NULL     |    NULL |                NULL | NULL  | NULL      | NULL       | NULL       | NULL           | NULL      | NULL                  | NULL          | NULL    |               NULL |
+----+-------------------+-------------+----------+--------------+-------------------+----------+------------------+--------------------+-----------------+----------------+----------------+---------------+----------------------+----------------------+-----------------------+----------------------+-----------------+-----------------+------------------+-------------------------+------------------------+----------+---------+---------------------+-------+-----------+------------+------------+----------------+-----------+-----------------------+---------------+---------+--------------------+


INSERT INTO icinga_host(object_name, object_type, disabled, address)
VALUES('Yahoo',  'object', 'n',  'yahoo.com');



select * from  icinga_host_inheritance;
+---------+----------------+--------+
| host_id | parent_host_id | weight |
+---------+----------------+--------+
|       7 |              6 |      1 |
|       8 |              6 |      1 |
+---------+----------------+--------+

INSERT INTO icinga_host_inheritance(host_id,parent_host_id ,weight)
VALUES(9,6,1);


select * from icinga_service;
+----+------------------+-------------+----------+--------------+---------+----------------+------------------+--------------------+-----------------+----------------+----------------+---------------+----------------------+----------------------+-----------------------+----------------------+-----------------+-----------------+------------------+-------------------------+------------------------+----------+---------+---------------------+-------+-----------+------------+------------+----------------+-----------+-----------+-------------------+---------------+--------------------+
| id | object_name      | object_type | disabled | display_name | host_id | service_set_id | check_command_id | max_check_attempts | check_period_id | check_interval | retry_interval | check_timeout | enable_notifications | enable_active_checks | enable_passive_checks | enable_event_handler | enable_flapping | enable_perfdata | event_command_id | flapping_threshold_high | flapping_threshold_low | volatile | zone_id | command_endpoint_id | notes | notes_url | action_url | icon_image | icon_image_alt | use_agent | apply_for | use_var_overrides | assign_filter | template_choice_id |
+----+------------------+-------------+----------+--------------+---------+----------------+------------------+--------------------+-----------------+----------------+----------------+---------------+----------------------+----------------------+-----------------------+----------------------+-----------------+-----------------+------------------+-------------------------+------------------------+----------+---------+---------------------+-------+-----------+------------+------------+----------------+-----------+-----------+-------------------+---------------+--------------------+
|  5 | service-template | template    | n        | NULL         |    NULL |           NULL |              175 |               NULL |            NULL | NULL           | NULL           |          NULL | NULL                 | NULL                 | NULL                  | NULL                 | NULL            | NULL            |             NULL |                    NULL |                   NULL | NULL     |    NULL |                NULL | NULL  | NULL      | NULL       | NULL       | NULL           | NULL      | NULL      | NULL              | NULL          |               NULL |
|  6 | service-template | object      | n        | NULL         |       7 |           NULL |             NULL |               NULL |            NULL | NULL           | NULL           |          NULL | NULL                 | NULL                 | NULL                  | NULL                 | NULL            | NULL            |             NULL |                    NULL |                   NULL | NULL     |    NULL |                NULL | NULL  | NULL      | NULL       | NULL       | NULL           | NULL      | NULL      | NULL              | NULL          |               NULL |
|  7 | service-template | object      | n        | NULL         |       8 |           NULL |             NULL |               NULL |            NULL | NULL           | NULL           |          NULL | NULL                 | NULL                 | NULL                  | NULL                 | NULL            | NULL            |             NULL |                    NULL |                   NULL | NULL     |    NULL |                NULL | NULL  | NULL      | NULL       | NULL       | NULL           | NULL      | NULL      | NULL              | NULL          |               NULL |
+----+------------------+-------------+----------+--------------+---------+----------------+------------------+--------------------+-----------------+----------------+----------------+---------------+----------------------+----------------------+-----------------------+----------------------+-----------------+-----------------+------------------+-------------------------+------------------------+----------+---------+---------------------+-------+-----------+------------+------------+----------------+-----------+-----------+-------------------+---------------+--------------------+

INSERT INTO icinga_service(object_name, object_type, disabled, host_id)
VALUES('service-template', 'object', 'n', 9);


use director;
select * from  icinga_host;  
select * from  icinga_host_inheritance;  
select * from icinga_service; 


-- Agrengado un Host
INSERT INTO icinga_host(object_name, object_type, disabled, address)
VALUES('Yahoo',  'object', 'n',  'yahoo.com');

-- Agregando el template que ocupa el host, 
-- host_id: Indica el id con que se guardo el Host, select max(id) from icinga_host;
-- parent_host_id: Id del templete-host ocupado
-- weight: Por defecto 1
INSERT INTO icinga_host_inheritance(host_id,parent_host_id ,weight)
VALUES(9,6,1);


--Agregando el servicio que ocupara el host
-- object_name: nombre del service-template que ocupara el host
-- object_type: por default object
-- diabled: por defaul n
-- host_id: Indica el id con que se guardo el Host, select max(id) from icinga_host;
INSERT INTO icinga_service(object_name, object_type, disabled, host_id)
VALUES('service-template', 'object', 'n', 9);
