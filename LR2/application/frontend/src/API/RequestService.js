import RefreshService from "./RefreshService";
import TokenController from "../controllers/TokenController.js";

const BASE_SERVER_URL = "http://localhost:5000/";

const IsJSONstring = (str) => {
    try {
        const p = JSON.parse(str);
    } catch(e) {
        return false;
    }
    return true;
}

export const MakeRequest = async (endpoint, requestOptions) => {
    if (!endpoint.startsWith(BASE_SERVER_URL)) {
        endpoint = BASE_SERVER_URL + endpoint
    }
    let response = await fetch(endpoint, requestOptions);
    let data = await response.text();
    let responseData = {
        status: response.status,
        data: data
    };
    if (IsJSONstring(data)) {
        responseData.data = JSON.parse(data);
    }
    return responseData;
}

export const MakeAuthorizedRequest = async (endpoint, requestOptions, refreshed) => {
    //console.log(endpoint, requestOptions)
    let response = await MakeRequest(endpoint, requestOptions);
    if (response.status === 401 && !refreshed) {
        let response = await RefreshService.refresh();
        if (response.status === 200) {
            TokenController.setToken(response.data.access_token);
            requestOptions.headers['Authorization'] = TokenController.getToken();
            return await MakeAuthorizedRequest(endpoint, requestOptions, true);
        } else {
            if (response.status === 401) {
                //window.location.href = "http://localhost:3000/enter";
            }
        }
        return response;
    }
    return response;
}