import React from 'react';
import {useLocation} from "react-router-dom";
import LoginPage from "./login/Login";
import RegisterPage from "./register/Registration";
import "./Form.css";

const AuthRootComponent = () => {
    const location = useLocation()
    return (
            <div className="form">
                    {location.pathname === '/enter' ? <LoginPage /> : location.pathname === '/register' ? <RegisterPage style /> : null}
            </div>
    )
    };

export default AuthRootComponent;