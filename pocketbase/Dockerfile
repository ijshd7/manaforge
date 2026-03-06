FROM alpine:3.19

ARG PB_VERSION=0.36.6

RUN apk add --no-cache wget unzip ca-certificates && \
    wget -q "https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_linux_amd64.zip" \
        -O /tmp/pb.zip && \
    unzip -q /tmp/pb.zip -d /pb && \
    chmod +x /pb/pocketbase && \
    rm /tmp/pb.zip

COPY entrypoint.sh /pb/entrypoint.sh
RUN chmod +x /pb/entrypoint.sh

WORKDIR /pb

EXPOSE 8090

ENTRYPOINT ["/pb/entrypoint.sh"]
