import React,  { useState } from 'react'
import title from './RegisterTitleText.module.css';
import '../jeneralStyles/FieldStyle.css';
import '../jeneralStyles/ButtonStyle.css';
import '../jeneralStyles/textsStyles/Label.css';
import '../jeneralStyles/textsStyles/AlignText.css';
import FormInput from '../FormInput.jsx';
import paragraph from  './SubtitleStyle.module.css';
import { NavLink } from 'react-router-dom';
import RegisterService from '../../../API/RegisterService';

const RegisterPage = () => {
    const [values, setValues] = useState({
        login: '',
        password: '',
        email: '',
    })

    const [value, setValue] = useState({
        repeatPassword: ''
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
            id:'email',
            type: 'text',
            name: 'email',
            placeholder:'Введите ваш e-mail адрес',
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
        },
        {
            id:'repeatPassword',
            type: 'password',
            name: 'repeatPassword',
            placeholder:'Повторите пароль',
            errorMessage: 'Пароли не совпадают',
            pattern: values.password,
            required: true
        }
    ]

    const onChange = (e) => {
        setValues({...values, [e.target.name]:e.target.value});
        setValue({...value, [e.target.name]:e.target.value});
    }

    async function sendRegisterRequest(e){
        e.preventDefault()
        if(values.login && values.password && values.email){
            await RegisterService.register(values)
            if(localStorage.getItem('ACCESS'))
            {
                window.location.href = "http://localhost:3000/contests"
            }
            else
            {
                alert("Ошибка. Проверьте корректность введенных данных и повторите попытку")
            }
        }
    }

    return (
        <div>
            <form className='authform'>
                <h1 className={title.registerTitle}>  
                    Регистрируйся
                </h1>

                <p className={paragraph.subtitle}>И участвуй в различных контестах</p>
                {inputs.map((input) => (
                    <FormInput 
                        className="field" 
                        key = {input.id} 
                        {...input} 
                        value1 = {values[input.name]}
                        value2 = {value[input.name]}
                        onChange = {onChange}
                        
                    />
                ))}
                <button onClick={sendRegisterRequest} className="margins" type='submit' variant="contained">
                    <p className="button">Зарегистрироваться </p>
                </button>

                <label className="label"> Уже есть аккаунт?⠀
                <NavLink to = "/enter" className="alignText"> Войти </NavLink>  
                </label>

            </form>
        </div>
    )
}

export default RegisterPage