# URL 단축 서비스

URL 단축 서비스는 긴 URL을 짧게 단축하여 사용하고, 단축된 URL을 통해 원본 URL로 리디렉션하는 기능을 제공합니다. 또한, 단축 URL이 조회된 횟수를 추적합니다.

## 기술 스택

### 백엔드: FastAPI
- **API 엔드포인트**
  - **POST `/shorten`**: 원본 URL과 만료 기간을 입력받아 단축 URL을 반환합니다.
  - **GET `/{short_key}`**: `short_key`에 해당하는 원본 URL로 리디렉션합니다.
  - **GET `/stats/{short_key}`**: `short_key`에 해당하는 URL의 조회 수를 반환합니다.

### 데이터베이스
- **MySQL**
  - 변동이 없는 스키마를 다루기에 적합하며, 사용하기 간단하여 선택하였습니다.
- **Redis**
  - 고성능 오픈소스 캐시 서버로 무난하여 선택하였습니다.
  - `{short_key: URL 객체}` 형식으로 캐시를 저장합니다.
  - URL객체는 `json` 라이브러리를 통해 딕셔너리를 직렬화하여 저장하고 불러옵니다.
  - 캐싱 시간은 URL의 만료 기간을 넘지 않도록 설정합니다.
    - `ttl = min(ttl, 만료까지 남은 시간)`

### 캐싱 전략
- **Cache Aside 패턴**
  - GET 메소드에 한정하여 적용합니다.

### 기타 도구
- **SQLAlchemy**: 데이터베이스 상호작용을 위해 사용합니다.
- **Alembic**: 데이터베이스 마이그레이션을 위해 사용합니다.
- **Pytest**: 테스트를 위해 사용합니다.
- **Docker**: 컨테이너화를 위해 사용합니다.
- **Poetry**: 의존성 관리를 위해 사용합니다.

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

