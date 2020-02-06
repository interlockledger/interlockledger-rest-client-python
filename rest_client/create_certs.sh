# App_Registry
openssl req -x509 -days 365 -newkey rsa:2048 -keyout writer.pem -out writer.pem
openssl pkcs12 -export -in writer.pem -inkey writer.pem -out writer.pfx
il2 key import -i -c "writer.pfx" -k "password" -u "Action,Protocol" --app 1 -v "300,301,306,302,304,303,305,307"

il2 permission add -i -n Apollo -o "keyManager!" -w "keyManagerPassword" -c "5o9J56xOCtjL9C49Gs3KiFZ8QIRc6JvsI08WGNaWKM4" -a localhost writer