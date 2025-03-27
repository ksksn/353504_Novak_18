import {MakeRequest} from "./RequestService";
import TokenController from "../controllers/TokenController";

export default class RegisterService
{
    static async register(values){
        if(localStorage.getItem('ACCESS')){
            localStorage.removeItem('ACCESS')
        }
        let code = await getSHA256Hash(values.password)
        values.password = code;

        const requestOptions = {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(values),
            credentials: 'include'
          };

        const response = await MakeRequest('register', requestOptions);
        if (response.status === 200) {
            const data = response.data;
            TokenController.setToken(data.access_token);
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