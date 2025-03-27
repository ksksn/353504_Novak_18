import TokenController from "../controllers/TokenController.js";
import { MakeRequest } from "./RequestService.js";

export default class RefreshService
{
    static async refresh(){
        const access_token = TokenController.extractToken();

        const requestOptions = {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': access_token
            },
            credentials: 'include'
        };

        let response = await MakeRequest('refresh', requestOptions)
        return response;
    }
}