import TokenController from "../controllers/TokenController";
import {MakeRequest} from "./RequestService";

export default class LoginService
{
    static async login(values){
        TokenController.extractToken();
        try {
            let code = await getSHA256Hash(values.password);
            let loginData = { password: code, login: values.login };
      
            const requestOptions = {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(loginData),
              credentials: 'include'
            };

            const response = await MakeRequest('login', requestOptions);
            if (response.status === 200) {
              const data = response.data;
              TokenController.setToken(data.access_token);
              localStorage.setItem('ACCESS', data.access_token);
            } else {
                throw new Error("Request failed with status " + response.status);
            }
        } catch (error) {
            console.error("Error:", error);
        }
    }
}

const getSHA256Hash = async (input) => {
    const textAsBuffer = new TextEncoder().encode(input);
    const hashBuffer = await window.crypto.subtle.digest("SHA-256", textAsBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hash = hashArray
      .map((item) => item.toString(16).padStart(2, "0"))
      .join("");
    return hash;
  };