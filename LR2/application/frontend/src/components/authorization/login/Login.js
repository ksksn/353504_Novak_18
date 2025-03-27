import React, { useState } from 'react';
import  title from './LoginTitleText.module.css';
import '../jeneralStyles/FieldStyle.css';
import '../jeneralStyles/ButtonStyle.css';
import '../jeneralStyles/textsStyles/Label.css';
import '../jeneralStyles/textsStyles/AlignText.css';
import { NavLink } from 'react-router-dom';
import FormInput from '../FormInput.jsx';
import LoginService from '../../../API/LoginService';

const LoginPage = () => {
    const [values, setValues] = useState({
        login: '',
        password: ''
    })

    const inputs = [
        {
            id:'login',
            type: 'text',
            name: 'login',
            placeholder:'Введите имя пользователя',
            errorMessage: 'Данное поле должно быть заполнено',
            minLength:'4',
            required: true
        },
        {
            id:'password',
            type: 'password',
            name: 'password',
            errorMessage: 'Данное поле должно быть заполнено',
            placeholder:'Введите пароль',
            minLength:'6',
            required: true
        }
    ]

    const onChange = (e) => {
        setValues({...values, [e.target.name]:e.target.value});
    }
    
    async function sendLoginRequest(e){
        e.preventDefault()
        if(values.login && values.password){
            try {
                await LoginService.login(values)
                if(localStorage.getItem('ACCESS'))
                {
                    window.location.href = "http://localhost:3000/contests"
                }
                else
                {
                    alert("Ошибка. Проверьте корректность введенных данных и повторите попытку")
                }
            } catch(error){
                if (error.response && error.response.status === 401) {
                    try {
                      await LoginService.refreshAccessToken();
                      await sendLoginRequest(e);
                    } catch (error) {
                      console.error(error);
                      alert('Ошибка при обновлении токена доступа.');
                    }
                  } else {
                    console.error(error);
                    alert('Ошибка. ' + error.message);
                }
            }
        }
    }

    return (
        <div> 
            <form className='authform'>
                <h1 className={title.loginTitle}>
                    Вход
                </h1>
                {inputs.map((input) => (
                    <FormInput 
                        className="field" 
                        key = {input.id} 
                        {...input} 
                        value = {values[input.name]}
                        onChange = {onChange}
                    />
                ))}

                <button onClick={sendLoginRequest} className="margins" type='submit' variant="contained">
                <p className="button"> Войти </p>
                </button>

                <label className="label"> Еще нет аккаунта?⠀
                    <NavLink to = "/enter" className="alignText"> Зарегистрироваться</NavLink>   
                </label>
            </form>
        </div>
    )
}

export default LoginPage