import jwt_decode from 'jwt-decode';

export default class TokenController {
    static setToken(token) {
        console.log()
        localStorage.setItem('ACCESS', token);
    }
    static extractToken() {
        let token = this.getToken();
        if (token) {
            localStorage.removeItem("ACCESS");
        }
        return token;
    }
    static getToken() {
        return localStorage.getItem("ACCESS");
    }

    static getDecodedToken() {
        return jwt_decode(this.getToken())
    }

    static getUserStatus() {
        return this.getDecodedToken().status
    }

    static isAdmin() {
        return this.getUserStatus() === 4;
    }

    static getUserNickname() {
        return this.getDecodedToken().user
    }
  }
  