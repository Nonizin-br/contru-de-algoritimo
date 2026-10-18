import os
import requests
import folium
from dotenv import load_dotenv


load_dotenv(".env")
token = os.getenv("SPTRANS_TOKEN")

if not token:
    print("Token não encontrado. Confira o arquivo .env.")
else:
    # Cria uma sessão e autentica na API Olho Vivo.
    s = requests.Session()

    res = s.post(
        f"http://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar"
        f"?token={token}"
     )

    if res.json():
        # Código da linha 139A (Lapa -> Vila Iório).
        # É diferente do código 2506 usado nos slides.
        codigo_linha = 2451

        # Busca as paradas da linha.
        res = s.get(
            "http://api.olhovivo.sptrans.com.br/v2.1/"
            "Parada/BuscarParadasPorLinha"
            f"?codigoLinha={codigo_linha}"
         )
        paradas = res.json()

        print("Quantidade de paradas:", len(paradas))

        if paradas:
            # Busca as posições dos ônibus em tempo real.
            res = s.get(
                "http://api.olhovivo.sptrans.com.br/v2.1/"
                "Posicao/Linha"
                f"?codigoLinha={codigo_linha}"
             )
            posicoes = res.json()
            onibus = posicoes.get("vs", [])

            # Cria o mapa centrado na primeira parada.
            m = folium.Map(
                location=[paradas[0]["py"], paradas[0]["px"]],
                zoom_start=14,
                tiles=None
            )

            # Adiciona o mapa-base público do OpenStreetMap.
            folium.TileLayer(
                tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                attr="© OpenStreetMap contributors",
                name="OpenStreetMap"
             ).add_to(m)

            # Adiciona as paradas com pins azuis.
            for parada in paradas:
                folium.Marker(
                    location=[parada["py"], parada["px"]],
                    popup=parada["np"],
                    icon=folium.Icon(color="blue")
                ).add_to(m)

            # Adiciona os ônibus em circulação com pins vermelhos.
            for veiculo in onibus:
                folium.Marker(
                    location=[veiculo["py"], veiculo["px"]],
                    popup=f"Ônibus {veiculo['p']}",
                    icon=folium.Icon(
                        color="red",
                        icon="bus",
                        prefix="fa"
                    )
                ).add_to(m)

            # Salva o mapa na mesma pasta deste arquivo.
            m.save("mapa_onibus.html")

            print("Mapa salvo como mapa_onibus.html")
            print("Ônibus encontrados:", len(onibus))

        else:
            print("A API não retornou paradas para essa linha.")

    else:
        print("Falha na autenticação. Confira o token no arquivo .env.")
