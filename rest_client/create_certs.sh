# App_Registry
openssl req -x509 -days 365 -newkey rsa:2048 -keyout writer.pem -out writer.pem
openssl pkcs12 -export -in writer.pem -inkey writer.pem -out writer.pfx
il2 key import -i -c "writer.pfx" -k "password" -u "Action,Protocol" --app 1 -v "300,301,306,302,304,303,305,307"

openssl req -x509 -days 365 -newkey rsa:2048 -keyout mykeymanager.pem -out mykeymanager.pem
openssl pkcs12 -export -in mykeymanager.pem -inkey mykeymanager.pem -out mykeymanager.pfx
il2 key import -i -c "mykeymanager.pfx" -k "password" -u "KeyManagement,Action,Protocol" --app 2 -v "500,501"

openssl req -x509 -days 365 -newkey rsa:2048 -keyout interlocker.pem -out interlocker.pem
openssl pkcs12 -export -in interlocker.pem -inkey interlocker.pem -out interlocker.pfx
il2 key import -i -c "interlocker.pfx" -k "password" -u "ForceInterlock,Action,Protocol" --app 3 -v "600,601"



il2 permission add -i -n Apollo -o "keyManager!" -w "keyManagerPassword" -c "5o9J56xOCtjL9C49Gs3KiFZ8QIRc6JvsI08WGNaWKM4" -a localhost writer