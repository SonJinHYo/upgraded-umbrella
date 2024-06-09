# URL Shortner Service
URL 단축 서비스는 긴 URL을 짧게 단축하여 사용하고, 단축된 URL을 통해 원본 URL로 리디렉션하는 기능을 제공합니다.

## Skill Stack
- Backend: FastAPI
  - API
    - POST `/shorten`: 원본 url과 유효 기간을 입력받아 단축url 반환
    - GET `/{short_key}`: `short_key`에 해당하는 url로 리다이렉트
    - GET `/stats/{short_key}`: `short_key`에 해당하는 url의 조회 수 반환
- Database:
  - MySQL: 변동이 없는 스키마를 다룬다는 점에서 관계형 DB 사용. 그 중 비교적 간단하게 시작 가능한 MySQL을 선택
  - Redis: 캐시 서버 중 무난한 고성능 오픈소스 선택
    - `{short_key: URL object}`로 캐시 저장
    - 캐싱 시간은 만료 기간을 넘지 않도록 구현
      - `ttl = min(ttl, 만료까지 남은 시간)`
- GET메소드에 한정해서 cache aside로 구현 
- ETC:
  - sqlalchemy, alembic
  - pytest
  - Docker
  - Poetry

</br>

----
 
## Running
1. git clone 후 fastapi, redis, mysql db 실행 (fastapi 실행 전 pytest 자동 진행)
```
git clone https://github.com/SonJinHYo/url-shortner.git
cd url-shortner
docker compose up --build
```
2. API Swagger 문서 접속
```
localhost:8000/docs
```

