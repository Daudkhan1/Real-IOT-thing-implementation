For Mosquito Implementation we can use the below publish and subscribe commands
according to our location of the Certs and private key.


mosquitto_sub -h alf679etvm4fm-ats.iot.ap-south-1.amazonaws.com -p 8883 \
--cafile /home/ubuntu/certs/AmazonRootCA1.pem \
--cert /home/ubuntu/certs/thing1.pem.crt \
--key /home/ubuntu/certs/thing1.pem.key \
-i thing1-client-sub \
-t "thing1/incoming" \
-d -v


mosquitto_pub -h alf679etvm4fm-ats.iot.ap-south-1.amazonaws.com -p 8883 \
  --cafile /home/ubuntu/certs/AmazonRootCA1.pem \
  --cert /home/ubuntu/certs/thing1.pem.crt \
  --key /home/ubuntu/certs/thing1.pem.key \
  -i thing1-client-pub -t "thing1/incoming" -m "Hello from MQTT publisher" -d
